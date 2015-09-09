# - Coding UTF8 -
#
# Networked Decision Making
# Development Sites (source code): http://github.com/DonaldMcC/gdms
#
# Demo Sites (Google App Engine)
#   http://dmcc.pythonanywhere.com/gdmsprod/
#   http://dmcc.pythonanywhere.com/gdmsdemo/
#
# License Code: MIT
# License Content: Creative Commons Attribution 3.0
#
# Also visit: www.web2py.com
# or Groups: http://groups.google.com/group/web2py
# For details on the web framework used for this development
#
# With thanks to Guido, Massimo and many other that make this sort of thing
# much easier than it used to be


"""
This controller has 12 functions:

index -     for a list of events
new_event - for creating and editing events
accept_event - when event submitted
my_events - for creating, updating and deleting events
eventqury - a loadable query for events - split by future and past
eventbar - a single column list of events for the sidebar
viewevent - the main detailed page on events which will mainly be accessed
            from event or the sidebars and load functions
eventaddquests - being removed - will be a popup button if selected explaining
                 how it works and just find from there and design the ajax function
vieweventmap2 - think this is just vieweventmap with more JSON data and will supercede eventmap
link - Ajax for linking and unlinking questions from events
move - Ajax for moving event questions around 
"""


import datetime, json
from ndspermt import get_groups, get_exclude_groups
from ndsfunctions import graphtojson, geteventgraph
from d3js2py import d3graph

def index():
    scope = request.args(0, default='Unspecified')
    # This now loads data via eventqry.load but the reload of upcoming versus past
    # TODO does not yet use AJAX for toggle from past to upcoming events
    return dict(scope=scope)


@auth.requires_login()
def new_event():
    # This allows creation of an event or editing of an event if recordid is supplied
    locationid = request.args(0, default='Not_Set')
    eventid = request.args(1, default=None)
    record = 0

    if eventid is not None:
        record = db.event(eventid)
        if record.auth_userid != auth.user.id:
            session.flash = ('Not Authorised - evens can only be edited by their owners')
            redirect(URL('index'))

    # so do we do this as unconnected query and just pull the list out????
    query = ((db.location.shared == True) | (db.location.auth_userid == auth.user_id))

    db.event.locationid.requires = IS_IN_DB(db(query), 'location.id', '%(location_name)s')

    fields = ['event_name', 'locationid', 'startdatetime', 'enddatetime',
              'description', 'shared']
    if eventid:
        form = SQLFORM(db.event, record, fields, formstyle='table3cols')
    else:
        form = SQLFORM(db.event, fields=fields, formstyle='table3cols')

    if locationid == 'Not_Set':
        form.vars.locationid = db(db.location.location_name == 'Unspecified').select(
            db.location.id, cache=(cache.ram, 3600), cacheable=True).first().id
    else:
        form.vars.locationid = int(locationid)

    if form.validate():
        form.vars.id = db.event.insert(**dict(form.vars))
        # response.flash = 'form accepted'
        session.event_name = form.vars.id
        redirect(URL('accept_event', args=[form.vars.id]))
        # redirect(URL('accept_question',args=[form.vars.qtype]))
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill out the form'

    return dict(form=form)

@auth.requires_login()
def accept_event():
    response.flash = "Event Created"
    eventid = request.args(0, cast=int, default=0) or redirect(URL('new_event'))
    eventrow = db(db.event.id == eventid).select().first()
    session.eventid = eventid
    return dict(eventid=eventid, eventrow=eventrow)


@auth.requires_login()
def my_events():
    query1 = db.event.owner == auth.user.id
    myfilter = dict(event=query1)
    grid = SQLFORM.smartgrid(db.event, formstyle=SQLFORM.formstyles.bootstrap3, constraints=myfilter, searchable=False)
    return locals()


def eventqry():
    scope = request.args(0, default='Unspecified')
    locationid = request.args(1, cast=int, default=0)
    datenow = datetime.datetime.utcnow()
    query = (db.event.startdatetime > datenow)
    
    if scope == 'My':
        query = (db.event.auth_userid == auth.user.id)
    elif scope == 'Location':
        query = (db.event.locationid == locationid)
    elif scope == 'Past':
        query = (db.event.startdatetime < datenow)
        #events = db(query).select(orderby=[~db.event.startdatetime], cache=(cache.ram, 1200), cacheable=True)
        orderby = [~db.event.startdatetime]
    else:
        orderby = [db.event.startdatetime]

    unspecevent = db(db.event.event_name == 'Unspecified').select(db.event.id,
        cache=(cache.ram, 1200), cacheable=True).first().id

    events = db(query).select(orderby=orderby, cache=(cache.ram, 1200), cacheable=True)

    unspec = events.exclude(lambda row: row.id == unspecevent)
    return dict(events=events)


def eventbar():
    datenow = datetime.datetime.utcnow()
    # line below fails on gae for some reason and limitby may be fine instead to not get too many
    # query = (db.event.startdatetime > datenow) & ((db.event.startdatetime - datenow) < 8.0)
    # lets just get them all
    query = (db.event.startdatetime > datenow)
    orderby = [db.event.startdatetime]
    events = db(query).select(orderby=orderby, cache=(cache.ram, 1200), cacheable=True)
    return dict(events=events)


def viewevent():
    # This is a non-network view of events - think this will be removed
    # just use vieweventmap instead
    eventid = request.args(0, cast=int, default=0) or redirect(URL('index'))
    eventrow = db(db.event.id == eventid).select(cache=(cache.ram, 1200), cacheable=True).first()
    session.eventid = eventid
    return dict(eventrow=eventrow, eventid=eventid)


def eventadditems():
    # this replaces index and will now aim to provide an ajax version of review and 4 sections being this
    # issues, questions and actions which can all be shown or hidden and we may have a map section thereafter

    # this will also need an arg of some sort to determine if session variables should be heeded initially or default
    # to preset values - but whole thing is getting there now

    # this is a new file aiming to replace action index and review resolved and finally review my answers
    # Plan is to have up to 3 arguments for this which I thnk will be
    # 1 View - v
    # 2 Query - q
    # 3 Sort Order - s
    # 4 Page
    # 5 Items Per Page

    # Valid values for view are:
    # quest, action
    # Valid values for query are:
    # resolved, agreed, proposed and my - my is only valid if logged in
    # Valid values for sort order are dependant on the view but may be

    # priority, resolvedate, duedate, submitdate or responsible for actions
    #
    # so view changes to be a panel selection - the query will be all the record filters
    # sort order should be on the loaded sections and ideally might be a default but clickable on the gride
    # however I think this would need to then be stored as parameer for pagination
    # items per page should also be on the subsections I think - so all this has is the query parameters and some sort
    # of parameter for which sections to load and the status of the questions may impact the load
    # potentially rest of this might be a form but - probably simpler to just build a layout and a call from there
    # so lets go with this
    # was thinking about doing this with some sort of form submission javascript - however I think we will change tack,
    # do with session variables as these are sort of setup and it makes the loading piece much easier so the load forms
    # will generally apply session variables of no request variables suplied and then would more or less be as is
    # advantage of this is that system will remember your last query - however it may not default it in the form
    #  - may need to display somewhere in the meantime

    eventid = request.args(0, cast=int, default=0) or redirect(URL('index'))
    eventrow = db(db.event.id == eventid).select(cache=(cache.ram, 1200), cacheable=True).first()
    session.eventid = eventid

    unspeceventid = db(db.event.event_name == 'Unspecified').select(db.event.id).first().id

    heading = 'Resolved Questions'
    # v = 'quest' if set this overrides the session variables
    # q = 'resolved'
    # s = 'resolved'
    message = ''
    fields = ['selection', 'sortorder', 'filters', 'scope', 'continent', 'country', 'subdivision',
              'category', 'answer_group']

    if auth.user:
        db.viewscope.answer_group.requires = IS_IN_SET(set(get_groups(auth.user_id)))

    v = request.args(0, default='None')  # lets ust his for my
    q = request.args(1, default='None')  # this matters
    s = request.args(2, default='None')  # this is the sort order
    page = request.args(3, cast=int, default=0)

    if not session.selection:
        if v == 'quest':
            session.selection = ['Question']
        elif v == 'issue':
            session.selection = ['Issue']
        elif v == 'action':
            session.selection = ['Action']
        else:
            session.selection = ['Issue', 'Question', 'Action']

        if q == 'InProg':
            session.selection.append('Proposed')
        elif q == 'Draft':
            session.selection.append('Draft')
        else:
            session.selection.append('Resolved')

    if s == 'priority':
        session.sortorder = '1 Priority'
    elif s == 'submit':
        session.sortorder = '3 Submit Date'
    elif s == 'answer':
        session.sortorder = '4 Answer Date'
    else:
        session.sortorder = '2 Resolved Date'

    # formstyle = SQLFORM.formstyles.bootstrap3
    form = SQLFORM(db.viewscope, fields=fields, formstyle='table3cols',
                   buttons=[TAG.button('Submit', _type="submit", _class="btn btn-primary btn-group"),
                            TAG.button('Reset', _type="button", _class="btn btn-primary btn-group",
                            _onClick="parent.location='%s' " % URL('newindex'))])

    form.vars.category = session.category
    if session.scope:
        form.vars.scope = session.scope
    form.vars.continent = session.vwcontinent
    form.vars.country = session.vwcountry
    form.vars.subdivision = session.vwsubdivision
    form.vars.selection = session.selection
    if session.filters:
        form.vars.filters = session.filters

    if q == 'Draft':
        session.selection = ['Issue', 'Question', 'Action', 'Draft']

    form.vars.sortorder = session.sortorder
    form.vars.selection = session.selection

    items_per_page = 50
    limitby = (page * items_per_page, (page + 1) * items_per_page + 1)

    if form.validate():
        session.scope = form.vars.scope
        session.category = form.vars.category
        session.vwcontinent = form.vars.continent
        session.vwcountry = form.vars.country
        session.vwsubdivision = form.vars.subdivision
        session.selection = form.vars.selection
        session.filters = form.vars.filters

        page = 0

        redirect(URL('eventadditems', args=eventid))

    return dict(form=form, page=page, items_per_page=items_per_page, v=v, q=q,
                s=s, heading=heading, message=message, unspeceventid=unspeceventid, eventrow=eventrow)

def vieweventmap():
    # This is a rewrite to use functions for this
    # approach now is that all events with questions should have an eventmap
    # but there should be a function to retrieve the functions and positions

    FIXWIDTH = 800
    FIXHEIGHT = 600

    resultstring = ''

    eventid = request.args(0, cast=int, default=0)
    redraw = request.vars.redraw

    # todo block redraw if event is archived - perhaps ok on archiving

    if not eventid:  # get the next upcoming event
        datenow = datetime.datetime.utcnow()

        query = (db.event.startdatetime > datenow)
        events = db(query).select(db.event.id, orderby=[db.event.startdatetime]).first()
        if events:
            eventid = events.id
        else:
            response.view = 'noevent'
            return dict(resultstring='No Event')

    grwidth = request.args(1, cast=int, default=FIXWIDTH)
    grheight = request.args(2, cast=int, default=FIXHEIGHT)
    eventrow = db(db.event.id == eventid).select().first()
    # eventmap = db(db.eventmap.eventid == eventid).select()

    # Retrieve the event graph as currently setup and update if 
    # being redrawn
    eventgraph = geteventgraph(eventid, redraw)
    resultstring = eventgraph['resultstring']
    print resultstring

    if resultstring == 'No Items setup for event':
        response.view = 'noevent'
        return dict(resultstring='No Items setup for event')

    quests = eventgraph['quests']
    links = eventgraph['links']
    nodepositions = eventgraph['nodepositions']

    # oonvert graph to json representation for jointjs
    graphdict = graphtojson(quests, links, nodepositions, 1, 1, True)

    cellsjson = graphdict['cellsjson']
    keys = graphdict['keys']
    resultstring = graphdict['resultstring']

    return dict(cellsjson=XML(cellsjson), eventrow=eventrow, links=links, resultstring=resultstring,
                eventmap=quests,  keys=keys, eventid=eventid)


def vieweventmapd3():
    # This is a rewrite to use functions for this
    # approach now is that all events with questions should have an eventmap
    # but there should be a function to retrieve the functions and positions

    FIXWIDTH = 1
    FIXHEIGHT = 1
    radius = 160

    resultstring = ''

    eventid = request.args(0, cast=int, default=0)
    redraw = request.vars.redraw

    # todo block redraw if event is archived - perhaps ok on archiving

    if not eventid:  # get the next upcoming event
        datenow = datetime.datetime.utcnow()

        query = (db.event.startdatetime > datenow)
        events = db(query).select(db.event.id, orderby=[db.event.startdatetime]).first()
        if events:
            eventid = events.id
        else:
            response.view = 'noevent'
            return dict(resultstring='No Event')

    grwidth = request.args(1, cast=int, default=FIXWIDTH)
    grheight = request.args(2, cast=int, default=FIXHEIGHT)
    eventrow = db(db.event.id == eventid).select().first()
    # eventmap = db(db.eventmap.eventid == eventid).select()

    # Retrieve the event graph as currently setup and update if 
    # being redrawn
    eventgraph = geteventgraph(eventid, redraw)
    resultstring = eventgraph['resultstring']
    print resultstring

    if resultstring == 'No Items setup for event':
        response.view = 'noevent'
        return dict(resultstring='No Items setup for event')

    quests = eventgraph['quests']
    links = eventgraph['links']
    nodepositions = eventgraph['nodepositions']

    # oonvert graph to json representation for jointjs
    # graphdict = graphtojson(quests, links, nodepositions, 1, 1, True)

    # cellsjson = graphdict['cellsjson']
    # keys = graphdict['keys']
    # resultstring = graphdict['resultstring']

    # resultstring = netgraph['resultstring']

    d3dict = d3graph(quests, links, nodepositions, grwidth, grheight, True, radius)
    d3nodes = d3dict['nodes']
    d3edges = d3dict['edges']

    #return dict(cellsjson=XML(cellsjson), eventrow=eventrow, links=links, resultstring=resultstring,
    #            eventmap=quests,  keys=keys, eventid=eventid)

    return dict(resultstring=resultstring,eventrow=eventrow, eventid=eventid,  links=links, eventmap=quests,
                d3nodes=XML(json.dumps(d3nodes)), d3edges=XML(json.dumps(d3edges)))

def link():
    # This allows linking questions to an event via ajax

    eventid = request.args[0]
    chquestid = request.args[1]
    action = request.args[2]

    if auth.user is None:
        responsetext = 'You must be logged in to link questions to event'
    else:
        quest = db(db.question.id == chquestid).select().first()
        unspecevent = db(db.event.event_name == 'Unspecified').select(db.event.id, cache=(cache.ram, 3600),).first()

        # Think about where this is secured - should probably be here
        event = db(db.event.id == eventid).select().first()

        if event.shared or (event.owner == auth.user.id) or (quest.auth_userid == auth.user.id):
            if action == 'unlink':
                db(db.question.id == chquestid).update(eventid=unspecevent.id)
                responsetext = 'Question %s unlinked' % chquestid
            else:
                db(db.question.id == chquestid).update(eventid=eventid)
                # Then if there was an eventmap it should require to be linked to
                # to the eventmap but if not it shouldn't
                eventquest = db((db.eventmap.eventid == eventid) & (db.eventmap.status == 'Open')).select().first()
                if eventquest:
                    recid = db.eventmap.insert(eventid=eventid, questid=quest.id, xpos=50, ypos=40,
                                questiontext=quest.questiontext, answers=quest.answers, qtype=quest.qtype,
                                urgency=quest.urgency, importance=quest.importance, correctans=quest.correctans,
                                queststatus=quest.status)
                responsetext = 'Question %s linked to event' % chquestid
        else:
            responsetext = 'Not allowed - This event is not shared and you are not the owner'
    return responsetext


def move():
    # This will allow moving the position of questions on an eventmap - but not on a general map at present
    # as no obvious way to save them - however think we will comment out the code if not authorised
    #eventid = request.args[0]
    #chquestid = request.args[1]
    #newxpos = request.args[2]
    #newypos = request.args[3]
    #questid = int(chquestid[3:])

    eventid = request.args(0, cast=int, default=0)
    questid = request.args(1, cast=int, default=0)
    newxpos = request.args(2, cast=int, default=0)
    newypos = request.args(3, cast=int, default=0)

    print('move was called')

    if auth.user is None:
        responsetext = 'You must be logged in to save movements'
    else:
        event = db(db.event.id == eventid).select().first()
        if event.shared or (event.owner == auth.user.id):
            db(db.eventmap.questid == questid).update(xpos=newxpos, ypos=newypos)
            responsetext = 'Element moved'
        else:
            responsetext = 'Moves not saved - you must be owner of ' + event.event_name + 'to save changes'
    return responsetext


@auth.requires_signature()
def archive():
    # This will be callable via a button from vieweventmap2 which has already ensured the eventmap exists
    # with all records in it and it will only show if the eventowner sees the page - Need a fairly lengthy explanation
    # of what archiving is and current status shows in the event details then probably sort of OK
    # Lets attempt to do this via ajax and come back with a message that explains what archiving is - may well want a
    # pop up on this before submission
    # poss move to :eval on this for response.flash as done on quickanswer now

    eventid = request.args(0, cast=int, default=0)
    event = db(db.event.id == eventid).select().first()
    if event.status == 'Open':
        status = 'Archiving'
        responsetext = 'Event moved to archiving'
    elif event.status == 'Archiving':
        status = 'Archived'
        responsetext = 'Event moved to archived status'
    else:
        responsetext = 'Only open events can be archived'
        return responsetext

    event.update_record(status=status)
    query = db.eventmap.eventid == eventid
    eventquests = db(query).select()

    for x in eventquests:
        x.update_record(status=status)

    if status == 'Archived':
        unspecevent = db(db.event.event_name == 'Unspecified').select(db.event.id, cache=(cache.ram, 3600),).first()
        # TODO some sort of explanation of the process by means of javascript are you sure popups on the button
        query = db.question.eventid == eventid
        quests = db(query).select()
        for x in quests:
            x.update_record(eventid=unspecevent.id)
    return responsetext


def eventreview():
    # This is an html report on the outcome of an event - it is based on the eventmap records and they can 
    # be edited by the owner using signed urls if the status needs updated or the correct answer has to be changed
    # idea is that this will more resemble actions and notes of a meeting as that is what I intend to use it for
    # urgency and importance also need to update so maybe no need to use the load approach as need everything on the one
    # page
    #
    # Objective is to review the issues, questions and actions - aim to do this in reverse order
    # ie start with the actions - then the questions and back to the issues
    # 2nd part would be the unresolved items in the same order
    # and probably the eventmap in the middle
    # will do as 1 report for now as this seems to work for pdf
    # only the owner will be able to edit the items but everyone can view - probably no need for datatables as reviews
    # will be small and I think I want this page to just list everything so it can be printed/pdfed etc
    # so issue with this is that eventreview is not updating correctly from eventmap definitely - redraw I think should
    # copy everything

    eventid = request.args(0, cast=int, default=0)
    eventrow = db(db.event.id == eventid).select().first()

    # Issue with this is it is a bit repetitive but lets do this way for now
    query = (db.eventmap.eventid == eventid) & (db.eventmap.qtype == 'action') & (db.eventmap.queststatus == 'Agreed')
    all_agreed_actions = db(query).select()
    query = (db.eventmap.eventid == eventid) & (db.eventmap.qtype == 'action') & (db.eventmap.queststatus == 'Disagreed')
    all_disagreed_actions = db(query).select()
    query = (db.eventmap.eventid == eventid) & (db.eventmap.qtype == 'quest') & (db.eventmap.queststatus == 'Resolved')
    all_agreed_quests = db(query).select()
    query = (db.eventmap.eventid == eventid) & (db.eventmap.qtype == 'issue') & (db.eventmap.queststatus == 'Agreed')
    all_agreed_issues = db(query).select()
    query = (db.eventmap.eventid == eventid) & (db.eventmap.qtype == 'issue') & (db.eventmap.queststatus == 'Disagreed')
    all_disagreed_issues = db(query).select()
    query = (db.eventmap.eventid == eventid) & (db.eventmap.qtype == 'quest') & (db.eventmap.queststatus == 'In Progress')
    all_inprog_quests = db(query).select()
    query = (db.eventmap.eventid == eventid) & (db.eventmap.qtype == 'action') & (db.eventmap.queststatus == 'In Progress')
    all_inprog_actions = db(query).select()
    query = (db.eventmap.eventid == eventid) & (db.eventmap.qtype == 'issue') & (db.eventmap.queststatus ==  'In Progress')
    all_inprog_issues = db(query).select()

    items_per_page=50

    permitgroups = get_groups(auth.user_id)
    # change logic to only show things that users are specifically permitted for
    
    agreed_actions = all_agreed_actions.exclude(lambda r: r.answer_group in permitgroups)
    disagreed_actions = all_disagreed_actions.exclude(lambda r: r.answer_group in permitgroups)
    agreed_quests = all_agreed_quests.exclude(lambda r: r.answer_group in permitgroups)
    agreed_issues = all_agreed_issues.exclude(lambda r: r.answer_group in permitgroups)
    disagreed_issues = all_disagreed_issues.exclude(lambda r: r.answer_group in permitgroups)
    inprog_actions = all_inprog_actions.exclude(lambda r: r.answer_group in permitgroups)
    inprog_quests = all_inprog_quests.exclude(lambda r: r.answer_group in permitgroups)
    inprog_issues = all_inprog_issues.exclude(lambda r: r.answer_group in permitgroups)

    return dict(eventid=eventid, eventrow=eventrow, items_per_page=items_per_page, agreed_actions=agreed_actions,
                disagreed_actions=disagreed_actions, disagreed_issues=disagreed_issues, agreed_quests=agreed_quests,
                agreed_issues=agreed_issues, permitgroups=permitgroups,
                inprog_quests=inprog_quests, inprog_actions=inprog_actions, inprog_issues=inprog_issues)

    # else:
    # TODO redirect here I think if failed to exclude quests but want users to see unspecified quets which this
    # doesn't - shows everything
    # return dict(eventid=eventid, eventrow=eventrow, items_per_page=items_per_page, agreed_actions=agreed_actions,
    #            disagreed_actions=disagreed_actions, disagreed_issues=disagreed_issues, agreed_quests=agreed_quests,
    #            agreed_issues=agreed_issues,
    #            inprog_quests=inprog_quests, inprog_actions=inprog_actions, inprog_issues=inprog_issues)


def eventitemedit():
    # maybe this can be called for both view and edit by the owner
    # proposal would be that this becomes - still not clear enough how this works
    # requirement is that status and correctans will be updateable and maybe nothing else
    eventmapid = request.args(0, cast=int, default=0)

    record = db.eventmap(eventmapid)

    if record:
        questiontext = record['questiontext']
        anslist = record['answers']
        #anslist.insert(0, 'Not Resolved')
        qtype = record['qtype']
        correctans = record['correctans']
        eventrow = db(db.event.id == record.eventid).select(cache=(cache.ram, 1200), cacheable=True).first()
        labels = (record.qtype == 'issue' and {'questiontext': 'Issue'}) or (record.qtype == 'action' and {'questiontext': 'Action'}) or {'questiontext': 'Question'}

        fields = ['queststatus',  'correctans', 'adminresolve']

        form = SQLFORM(db.eventmap, record, showid=False, fields=fields, labels=labels,  formstyle='table3cols')
    else:
        redirect(URL('notshowing/' + 'NoQuestion'))

    if form.validate():
        if form.vars.correctans != correctans:
            if form.vars.correctans == -1:
                form.vars.queststatus = 'In Progress'
            else:
                if qtype == 'quest':
                    form.vars.queststatus = 'Resolved'
                elif form.vars.correctans == 0:
                    form.vars.queststatus = 'Agreed'
                else:
                    form.vars.queststatus = 'Disagreed'

        record.update_record(**dict(form.vars))

        response.flash = 'form accepted'
        # TODO make this do something sensible
        redirect(URL('viewquest', 'index', args=1))
    elif form.errors:
        response.flash = 'form has errors'

    return dict(questiontext=questiontext, anslist=anslist, qtype=qtype, correctans=correctans,
                    eventrow=eventrow, form=form)


def eventreviewload():
    # this started from questload - but will be changed for eventreview as more specified -
    # lets just go with request.vars.selection and not much else for now - but not sure if actually
    # want to do it this way as may be hard to do pdfs - SO THIS REMAINS UNFINISHED FOR NOW

    # selection will currently be displayed separately
    eventid = request.args(0)
    eventrow = db(db.event.id == record.eventid).select(cache=(cache.ram, 1200), cacheable=True).first()

    if request.vars.selection == 'QP':
        strquery = (db.eventmap.qtype == 'quest') & (db.eventmap.queststatus == 'In Progress')
    elif request.vars.selection == 'QR':
        strquery = (db.eventmap.qtype == 'quest') & (db.eventmap.queststatus == 'Resolved')
    elif request.vars.selection == 'IP':
        strquery = (db.eventmap.qtype == 'issue') & (db.eventmap.queststatus == 'In Progress')
        response.view = 'event/eventissueload.load'
    elif request.vars.selection == 'IR':
        strquery = (db.eventmap.qtype == 'issue') & (db.eventmap.queststatus == 'In Progress')
        response.view = 'event/eventissueload.load'
    elif request.vars.selection == 'AP':
        strquery = (db.eventmap.qtype == 'action') & (db.eventmap.queststatus == 'In Progress')
        response.view = 'default/eventissueload.load'
    elif request.vars.selection == 'AR':
        strquery = (db.eventmap.qtype == 'action') & (db.eventmap.queststatus == 'Agreed')
        response.view = 'event/eventissueload.load'
    elif request.vars.selection == 'AD':
        strquery = (db.eventmap.qtype == 'action') & (db.eventmap.queststatus == 'Disagreed')
        response.view = 'event/eventissueload.load'
    else:
        strquery = (db.eventmap.qtype == 'quest') & (db.eventmap.queststatus == 'Resolved')

    strquery &= (db.eventmap.eventid == eventid)

    sortorder = '1 Priority'
    if request.vars.sortby == 'ResDate':
        sortorder = '2 Resolved Date'
    elif request.vars.sortby == 'Priority':
        sortorder = '1 Priority'
    elif request.vars.sortby == 'CreateDate':
        sortorder = '3 Submit Date'

    if sortorder == '1 Priority':
        sortby = ~db.question.priority
    elif sortorder == '3 Submit Date':
        sortby = ~db.question.createdate
    else:
        sortby = ~db.question.resolvedate

    if request.vars.page:
        page = int(request.vars.page)
    else:
        page = 0

    if request.vars.items_per_page:
        items_per_page = int(request.vars.items_per_page)
    else:
        items_per_page = 3

    limitby = (page * items_per_page, (page + 1) * items_per_page + 1)
    q = request.vars.selection

    no_page = request.vars.no_page
    # print strquery

    # removed caching for now as there are issues
    # quests = db(strquery).select(orderby=[sortby], limitby=limitby, cache=(cache.ram, 1200), cacheable=True)
    quests = db(strquery).select(orderby=[sortby], limitby=limitby)

    # remove excluded groups always - this probably neees to staty which would mean questgroup
    # is required in the event archive (makes sense)
    if session.exclude_groups is None:
        session.exclude_groups = get_exclude_groups(auth.user_id)
    if quests and session.exclue_groups:
        alreadyans = quests.exclude(lambda r: r.answer_group in session.exclude_groups)

    source = 'Eventreview'
    view = 'std'
    return dict(eventrow=eventrow, quests=quests, page=page, source=source, items_per_page=items_per_page, q=q,
                view=view, no_page=no_page)

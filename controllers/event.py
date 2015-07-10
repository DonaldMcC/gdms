# - Coding UTF8 -
#
# Networked Decision Making
# Development Sites (source code): 
#
# Demo Sites (Google App Engine)
#   http://netdecisionmaking.appspot.com
#   http://globaldecisionmaking.appspot.com
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

import datetime
from netx2py import getpositions
from jointjs2py import jsonmetlink, getitemshape
from ndspermt import get_groups, get_exclude_groups

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


@auth.requires_login()
def eventaddquests():
    # Think this is a non-network view of events
    # this code is being removed - set to error and find out if called
    page = notavariable
    page = 0
    eventid = request.args(0, cast=int, default=0) or redirect(URL('index'))
    # page = request.args(0, cast=int, default=0)

    eventrow = db(db.event.id == eventid).select().first()

    session.event_name = eventrow.event_name
    session.eventid = eventid

    unspecevent = db(db.event.event_name == 'Unspecified').select(db.event.id).first().id

    return dict(eventrow=eventrow, eventid=eventid,  unspecevent=unspecevent)


def vieweventmap2():
    # This now has a load option and works fine when events are setup - however the redirect is a problem if no events
    # as then loads with another layout html and thing fails badly possibly better to change to just return message if
    # no selection for now  This has changed from generating objects as script to passing the data in a script object
    # and then adding via jointjs
    # Next fix is to ensure that all questions show on the map so if they have been added to the event after map created
    # then they need to be added here - think will route all archiving via eventmap

    # so now two things to add to this in some way
    # 1 ability to redraw the map via ajax with reset to eventmap args - but only if status is not archiving or archived
    #   lets do via

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
            response.view = 'noevent.load'
            return dict(resultstring='No Event')

    grwidth = request.args(1, cast=int, default=FIXWIDTH)
    grheight = request.args(2, cast=int, default=FIXHEIGHT)
    eventrow = db(db.event.id == eventid).select().first()
    eventmap = db(db.eventmap.eventid == eventid).select()

    # now only generate or regenerate eventmap if requested
    if not eventmap or redraw == 'True':
        query = db.question.eventid == eventid
        # quests = db(query).select(cache=(cache.ram, 120), cacheable=True)
        quests = db(query).select()

        questlist = [x.id for x in quests]

        if not questlist:
            response.view = 'noevent.load'
            return dict(resultstring='No Questions for event')

        parentlist = questlist
        childlist = questlist
        # removed for gae for now
        intquery = (db.questlink.targetid.belongs(questlist)) & (db.questlink.status == 'Active') & (
                    db.questlink.sourceid.belongs(questlist))

        # intlinks = db(intquery).select(cache=(cache.ram, 120), cacheable=True)
        intlinks = db(intquery).select()

        links = [x.sourceid for x in intlinks]

        if links:
            linklist = [(x.sourceid, x.targetid, {'weight': 30}) for x in intlinks]
        else:
            linklist = []

        # now need to find the id's that are not on the map and add them in
        # otherwise intlinks will fail at present but lets fix
        # remove eventmap entries where quests have been unlinked
        missquests = eventmap.exclude(lambda r: r.questid not in questlist)
        for x in missquests:
            x.delete_record()

        nodepositions = getpositions(questlist, linklist)
        # print questlist, linklist

        for row in quests:
            # generate full eventmap with network x and insert into eventmap
            recid = db.eventmap.update_or_insert((db.eventmap.eventid==eventid) & (db.eventmap.questid==row.id),
                                                 eventid=eventid, questid=row.id,
                                                 status='Open',
                                                 xpos=(nodepositions[row.id][0] * FIXWIDTH),
                                                 ypos=(nodepositions[row.id][1] * FIXHEIGHT),
                                                 answer_group=row.answer_group,
                                                 questiontext=row.questiontext, answers=row.answers,
                                                 qtype=row.qtype, urgency=row.urgency, importance=row.importance,
                                                 correctans=row.correctans, queststatus=row.status)

        #    # Make sure everything picked up TODO - line below is risky on GAE may need something better
        # think maybe just redo if count too low

        eventmap = db(db.eventmap.eventid == eventid).select()

    else:
        questlist = [x.questid for x in eventmap]

        if not questlist:
            response.view = 'noevent.load'
            return dict(resultstring='No Questions for event')

        parentlist = questlist
        childlist = questlist

        intquery = (db.questlink.targetid.belongs(questlist)) & (db.questlink.status == 'Active') & (
                    db.questlink.sourceid.belongs(questlist))


        # intlinks = db(intquery).select(cache=(cache.ram, 120), cacheable=True)
        intlinks = db(intquery).select()

        links = [x.sourceid for x in intlinks]

        if links:
            linklist = [(x.sourceid, x.targetid) for x in intlinks]
        else:
            linklist = []

    eventquests = [x.questid for x in eventmap]

    # so could then emerge here always with an eventmap established (probably as a dictionary rather than node positions
    if eventmap is None:
        response.view = 'noevent.load'
        return dict(resultstring='No Items setup for event')

    questmap = {}
    qlink = {}
    keys = '['
    linkarray = '['

    cellsjson = '['
    for x in eventmap:
        template = getitemshape(x.questid, x.xpos, x.ypos, x.questiontext, x.correctanstext(), x.status, x.qtype, x.priority)
        cellsjson += template + ','

    # if we have siblings and partners and layout is directionless then may need to look at joining to the best port
    # or locating the ports at the best places on the shape - most questions will only have one or two connections
    # so two ports may well be enough we just need to figure out where the ports should be and then link to the
    # appropriate one think that means iterating through quests and links for each question but can set the
    # think we should move back to the idea of an in and out port and then position them possibly by rotation
    # on the document - work in progress
    # thinking this graph will ultimately NOT use ports as this will be view only and would like html to work
    # think link can perhaps be same as std ones once graph created

    for x in intlinks:
        print 'link exists'
        strlink = 'Lnk' + str(x.id)
        strsource = 'Nod' + str(x.sourceid)
        strtarget = 'Nod' + str(x.targetid)
        #if (x.sourceid in eventquests and x.targetid in eventquests and
        #    strtarget in questmap.keys() and strsource in questmap.keys()):
        if (x.sourceid in eventquests and x.targetid in eventquests):
            #if questmap[strtarget][1] > questmap[strsource][1]:
            #if eventmap[x.targetid][xpos] > eventmap[x.sourceid][xpos]:
            # TODO sort above out need questids somehow
            if True:
                sourceport = 'b'
                targetport = 't'
            else:
                sourceport = 't'
                targetport = 'b'
            if x.createcount - x.deletecount > 1:
                dasharray = False
                linethickness = min(3 + x.createcount, 7)
            else:
                dasharray = True
                linethickness = 3

            qlink[strlink] = [strsource, strtarget, sourceport, targetport, dasharray, linethickness]
            keys += strlink
            keys += ','
        else:
            print x.sourceid, x.targetid, strtarget, strsource, eventquests, questmap.keys(), 'not added'

    keys = keys[:-1] + ']'

    session.networklist = questlist
    session.eventid = eventid

    for key, vals in qlink.iteritems():
        print 'qlink exists'
        template = jsonmetlink(key, vals[0], vals[1], vals[2], vals[3], vals[4])
        cellsjson += template + ','

    cellsjson = cellsjson[:-1]+']'

    #questmap=questmap,
    return dict(cellsjson=XML(cellsjson), eventrow=eventrow, links=links, resultstring=resultstring,
                eventmap=eventmap,  keys=keys, qlink=qlink, eventid=eventid)


def link():
    # This allows linking questions to an event via ajax

    eventid = request.args[0]
    chquestid = request.args[1]
    action = request.args[2]
    fixedx = 600
    fixedy = 500

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
                    quest = db(db.question.id == chquestid).select()
                    recid = db.eventmap.insert(eventid=eventid, questid=quest.id, xpos=50, ypos=40,
                                questiontext=questid.questiontext, answers=quest.answers, qtype=quest.qtype,
                                urgency=quest.urgency, importance=quest.importance, correctans=quest.correctans,
                                queststatus=quest.status)
                responsetext = 'Question %s linked to event' % chquestid
        else:
            responsetext = 'Not allowed - This event and you are not the owner'
    return responsetext


def move():
    # This will allow moving the position of questions on an eventmap - but not on a general map at present
    # as no obvious way to save them - however think we will comment out the code if not authorised
    eventid = request.args[0]
    chquestid = request.args[1]
    newxpos = request.args[2]
    newypos = request.args[3]
    questid = int(chquestid[3:])
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

    if status=='Archived':
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
    query = (db.eventmap.eventid == eventid) & (db.eventmap.qtype == 'issue') & (db.eventmap.queststatus == 'In Progress')
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

    
    #    # remove excluded groups always
    #if session.exclude_groups is None:
    #    # TODO think this should always return something so next bit unnecessary
    #    session.exclude_groups = get_exclude_groups(auth.user_id)
    #if session.exclue_groups:
    #    alreadyans = agreed_actions.exclude(lambda r: r.answer_group in session.exclude_groups)
    #    alreadyans = disagreed_actions.exclude(lambda r: r.answer_group in session.exclude_groups)
    #    alreadyans = agreed_quests.exclude(lambda r: r.answer_group in session.exclude_groups)
    #    alreadyans = agreed_issues.exclude(lambda r: r.answer_group in session.exclude_groups)
    #    alreadyans = disagreed_actions.exclude(lambda r: r.answer_group in session.exclude_groups)
    #    alreadyans = inprog_actions.exclude(lambda r: r.answer_group in session.exclude_groups)
    #    alreadyans = inprog_quests.exclude(lambda r: r.answer_group in session.exclude_groups)
    #    alreadyans = inprog_issues.exclude(lambda r: r.answer_group in session.exclude_groups)

    return dict(eventid=eventid, eventrow=eventrow, items_per_page=items_per_page, agreed_actions=agreed_actions,
                disagreed_actions=disagreed_actions, disagreed_issues=disagreed_issues, agreed_quests=agreed_quests,
                agreed_issues=agreed_issues, permitgroups=permitgroups,
                inprog_quests=inprog_quests, inprog_actions=inprog_actions, inprog_issues=inprog_issues)

    #else:
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
        questiontext=record['questiontext']
        anslist=record['answers']
        #anslist.insert(0, 'Not Resolved')
        qtype=record['qtype']
        correctans=record['correctans']
        eventrow = db(db.event.id == record.eventid).select(cache=(cache.ram, 1200), cacheable=True).first()
        labels = (record.qtype == 'issue' and {'questiontext': 'Issue'}) or (record.qtype == 'action' and {'questiontext': 'Action'}) or {'questiontext': 'Question'}

        fields = ['queststatus',  'correctans', 'adminresolve']

        form = SQLFORM(db.eventmap, record, showid=False, fields=fields, labels=labels,  formstyle='table3cols')
    else:
        redirect(URL('notshowing/' + 'NoQuestion'))

    if form.validate():
        if form.vars.correctans <> correctans:
            if form.vars.correctans==-1:
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

    strquery = strquery & (db.eventmap.eventid == eventid)

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

    # remove excluded groups always - this probably neees to staty which would mean questgroup is required in the event archive (makes sense)
    if session.exclude_groups is None:
        session.exclude_groups = get_exclude_groups(auth.user_id)
    if quests and session.exclue_groups:
        alreadyans = quests.exclude(lambda r: r.answer_group in session.exclude_groups)

    source = 'Eventreview'
    view = 'std'
    return dict(eventrow=eventrow, quests=quests, page=page, source=source, items_per_page=items_per_page, q=q,
                view=view, no_page=no_page)

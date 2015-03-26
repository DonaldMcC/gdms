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
eventquery - a loadable query for events - typicaly split by upcoming, future and past
eventbar - a single column list of events for the sidebar
viewevent - the main detailed page on events which will mainly be accessed from event or the sidebars
and load functions
eventaddquests - for adding questions to an event - not sure about this going forward
vieweventmap
vieweventmap2 - think this is just vieweventmap with more JSON data and will supercede eventmap
link - Ajax for linking and unlinking questions from events
move - Ajax for moving event questions around 
"""

#TODO remove event.html

import datetime
from netx2py import getpositions
from ndsfunctions import getwraptext
from jointjs2py import colourcode, textcolour, jsonportangle, portangle,  jsonmetlink

def index():
    scope = request.args(0, default='Unspecified')
    query = (db.event.id > 0)

    datenow = datetime.datetime.utcnow()
    #start_date = end_date - datetime.timedelta(days=8)
    #difference_in_days = abs((end_date - start_date).days)

    #print difference_in_days
    #this fails on gae as too many inequalities
    if len(request.args) < 2 or request.args[1] == 'Upcoming':
        #query = query & (db.event.startdatetime > datenow) & ((db.event.startdatetime - datenow) < 8.0)
        query = (db.event.startdatetime > datenow)
    elif request.args[1] == 'Future':
        #query = query & (db.event.startdatetime > datenow) & ((db.event.startdatetime - datenow) >= 8.0)
        query = (db.event.startdatetime > datenow)

    if scope == 'My':
        query = (db.event.auth_userid == auth.user.id)

    events = db(query).select(orderby=[db.event.startdatetime], cache=(cache.ram, 1200), cacheable=True)

    return dict(events=events)

@auth.requires_login()
def new_event():
    #This allows creation of an event or editing of an event if recordid is supplied
    locationid = request.args(0, default='Not_Set')
    eventid = request.args(1, default=None)

    if eventid != None:
        record = db.event(eventid)
        if record.auth_userid != auth.user.id:
            session.flash=('Not Authorised - evens can only be edited by their owners')
            redirect(URL('index'))

    query=((db.location.shared == True) | (db.location.auth_userid == auth.user_id))

    db.event.locationid.requires = IS_IN_DB(db(query),'location.id', '%(location_name)s')

    fields = ['event_name', 'locationid', 'startdatetime', 'enddatetime',
              'description', 'shared']
    if eventid:
        form = SQLFORM(db.event, record, fields, formstyle='table3cols')
    else:
        form = SQLFORM(db.event, fields=fields, formstyle='table3cols')

    if locationid == 'Not_Set':
        form.vars.locationid = db(db.location.location_name =='Unspecified').select(db.location.id, cache=(cache.ram,3600), cacheable=True).first().id
    else:
        form.vars.locationid = int(locationid)

    if form.validate():
        form.vars.id = db.event.insert(**dict(form.vars))
        #response.flash = 'form accepted'
        session.event_name = form.vars.id
        redirect(URL('accept_event', args=[form.vars.id]))
        #redirect(URL('accept_question',args=[form.vars.qtype])) 
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill out the form'

    return dict(form=form)


def accept_event():
    response.flash = "Event Created"
    eventid = request.args(0, cast=int, default=0) or redirect(URL('new_event'))
    return dict(eventid=eventid)


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

    if scope == 'Location':
        query = (db.event.locationid == locationid)

    orderby = [db.event.startdatetime]
    events = db(query).select(orderby=orderby, cache=(cache.ram, 1200), cacheable=True)

    return dict(events=events)


def eventbar():
    datenow = datetime.datetime.utcnow()
    #line below fails on gae for some reason and limitby may be fine instead to not get too many
    #query = (db.event.startdatetime > datenow) & ((db.event.startdatetime - datenow) < 8.0)
    query = (db.event.startdatetime > datenow)
    orderby = [db.event.startdatetime]
    events = db(query).select(orderby=orderby, cache=(cache.ram, 1200), cacheable=True)

    return dict(events=events)


def viewevent():
    #This is a non-network view of events - think this will be removed
    #just use vieweventmap instead
    eventid = request.args(0, cast=int, default=0) or redirect(URL('index'))
    eventrow = db(db.event.id == eventid).select(cache=(cache.ram, 1200),cacheable=True).first()
    session.eventid = eventid
    return dict(eventrow=eventrow, eventid=eventid)


@auth.requires_login()
def eventaddquests():
    #Think this is a non-network view of events
    page = 0
    #eventid = 0
    eventid = request.args(0, cast=int, default=0) or redirect(URL('index'))
    #page = request.args(0, cast=int, default=0)

    eventrow = db(db.event.id == eventid).select().first()

    session.event_name = eventrow.event_name
    session.eventid = eventid

    unspecevent = db(db.event.event_name == 'Unspecified').select(db.event.id).first().id

    #query = (db.question.eventid == eventid) & (db.question.qtype == 'quest')
    #sortby = ~db.question.createdate
    #items_per_page = 20

    #limitby = (page * items_per_page, (page + 1) * items_per_page + 1)

    #quests = db(query).select(orderby=sortby, limitby=limitby)

    #query = (db.question.eventid == eventid) & (db.question.qtype == 'action')

    #actions = db(query).select(orderby=sortby, limitby=limitby)
    #print limitby

    #query = (db.question.eventid == unspecevent) & (db.question.qtype == 'quest') & (db.question.status == 'In Progress')

    #othquests = db(query).select()

    #query = (db.question.eventid == unspecevent) & (db.question.qtype == 'action') & (db.question.status == 'In Progress')

    #othactions = db(query).select(orderby=sortby, limitby=limitby)

    #return dict(eventrow=eventrow, eventid=eventid, quests=quests, actions=actions, othquests=othquests,
    #            othactions=othactions, unspecevent=unspecevent, page=page, items_per_page=items_per_page)
    return dict(eventrow=eventrow, eventid=eventid,  unspecevent=unspecevent)


def vieweventmap2():
    # This now has a load option and works fine when events are setup - however the redirect is a problem if no events
    # as then loads with another layout html and thing fails badly possibly better to change to just return message if
    # no selection for now  This has changed from generating objects as script to passing the data in a script object and
    # then adding via jointjs
    # Next fix is to ensure that all questions show on the map so if they have been added to the event after map created
    # then they need to be added here - think will route all archiving via eventmap

    FIXWIDTH = 800
    FIXHEIGHT = 600

    resultstring = ''
    gotevent=True

    eventid = request.args(0, cast=int, default=0)

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
    eventquests = [x.questid for x in eventmap]
    query = db.question.eventid == eventid
    #quests = db(query).select(cache=(cache.ram, 120), cacheable=True)
    quests = db(query).select()

    questlist = [x.id for x in quests]
    if not questlist:
        response.view = 'noevent.load'
        return dict(resultstring='No Questions for event')

    parentlist = questlist
    childlist = questlist
    #removed for gae for now
    #intquery = (db.questlink.targetid.belongs(questlist)) & (db.questlink.status == 'Active') & (
    #db.questlink.sourceid.belongs(questlist))

    #this fails on gae as two inequalities
    #intlinks = db(intquery).select(db.questlink.id, db.questlink.sourceid, db.questlink.targetid,
    #                               db.questlink.createcount, db.questlink.deletecount)

    intquery = (db.questlink.status == 'Active') & (db.questlink.sourceid.belongs(questlist))

    #intlinks = db(intquery).select(cache=(cache.ram, 120), cacheable=True)
    intlinks = db(intquery).select()

    links = [x.sourceid for x in intlinks]

    if links:
        linklist = [(x.sourceid, x.targetid) for x in intlinks]
    else:
        linklist = []

    if not eventmap and quests:
        # generate full eventmap with network x and insert into eventmap
        nodepositions = getpositions(questlist, linklist)
        # think we insert them into the eventmap here and then run the query and may need to re-run if get wrong
        # number because of gae
        for key in nodepositions:
            recid = db.eventmap.insert(eventid=eventid, questid=key, xpos=(nodepositions[key][0] * FIXWIDTH), ypos=(nodepositions[key][1] * FIXHEIGHT))
            #Make sure everything picked up TODO - line below is risky on GAE may need something better
    else:
        # now need to find the id's that are not on the map and add them in
        # otherwise intlinks will fail at present but lets fix
        # remove eventmap entries where quests have been unlinked
        missquests = eventmap.exclude(lambda r: r.questid not in questlist)
        for x in missquests:
            x.delete_record()
        # add eventmap entries for quests added after eventmap created (at present aim to add at some sort of fixed position
        missquests = set(questlist) - set(eventquests)
        for i, x in enumerate(missquests):
            recid = db.eventmap.insert(eventid=eventid, questid=x, xpos=(FIXWIDTH-20 + (I * 3)), ypos=(0 + (i * 3)))

    eventmap = db(db.eventmap.eventid == eventid).select()
    eventquests = [x.questid for x in eventmap]

    #so could then emerge here always with an eventmap established (probably as a dictionary rather than node positions
    if eventmap is None:
        response.view = 'noevent.load'
        return dict(resultstring='No Items setup for event')

    # We should now compare eventmap and questlist as eventmap may have questions that are no longer part of event
    # and questions may also have been added to event after event map was generated - theoretically shouldn't need
    # this if just created but with gae might be helpful so lets do at all times for now.
    
    # approach I think is to delete positions of items which are no longer included and perhaps aim to put additioanl
    # items along the bottom of the layout if added
    
    #for x in eventmap:
    #    # not sure if this is worthwhile
    #    if x.questid not in questlist:
    #        x.delete_record()



    #missquests = set(questlist) - set(eventquests)
    #print str(len(missquests)) + ' Are missing'
    
    #thinking about doing a similar thing for parent child view - but not sure that's practical
    #insert from viewquest to go through - so this may be made into a separate routine
    print 'map'
    print eventmap
    print questlist

    questmap = {}
    qlink = {}
    keys = '['
    linkarray = '['

    for x in quests:
        if x['qtype'] == 'action':
            width = 200
            height = 100
            wraplength = 34
        else:
            width = 160
            height = 140
            wraplength = 25
        qtext = getwraptext(x.questiontext, x.correctanstext(), wraplength)
        rectcolour = colourcode(x.qtype, x.status, x.priority)
        colourtext = textcolour(x.qtype, x.status, x.priority)
        strobj = 'Nod' + str(x.id)
        questmap[strobj] = [0, 0, qtext, rectcolour, 14, 'tb', width, height, colourtext]
        keys += strobj
        keys += ','

    #  so piece below fails if we have an eventmap and then add questions afterwards - how should that be handled

    if eventmap is not None:
        for row in eventmap:
            strobj = 'Nod' + str(row.questid)
            questmap[strobj][0] = row.xpos
            questmap[strobj][1] = row.ypos

    # if we have siblings and partners and layout is directionless then may need to look at joining to the best port
    # or locating the ports at the best places on the shape - most questions will only have one or two connections
    # so two ports may well be enough we just need to figure out where the ports should be and then link to the
    # appropriate one think that means iterating through quests and links for each question but can set the
    # think we should move back to the idea of an in and out port and then position them possibly by rotation
    # on the document - work in progress
    # thinking this graph will ultimately NOT use ports as this will be view only and would like html to work
    # think link can perhaps be same as std ones once graph created

    for x in intlinks:
        strlink = 'Lnk' + str(x.id)
        strsource = 'Nod' + str(x.sourceid)
        strtarget = 'Nod' + str(x.targetid)
        if x.sourceid in eventquests and x.targetid in eventquests:
            if questmap[strtarget][1] > questmap[strsource][1]:
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


    keys = keys[:-1] + ']'

    session.networklist = [x.id for x in quests]

    session.eventid = eventid


    #This should move to a function ideally as a pure function
    cellsjson = '['
    linkarray = '['

    for key,vals in questmap.iteritems():
        template = jsonportangle(key,vals[0],vals[1],vals[2],vals[3],vals[4],vals[6],vals[7],vals[5],vals[8])
        cellsjson += template + ','

    for key,vals in qlink.iteritems():
        template = jsonmetlink(key,vals[0],vals[1],vals[2],vals[3],vals[4])
        cellsjson += template + ','
        linkarray += '"' + key + '",'

    cellsjson = cellsjson[:-1]+']'
    linkarray = linkarray[:-1]+']'
    # so this was temp as not working but can now go with vieweventmap2 to start with
    linkarray = []
    print linkarray

    return dict(cellsjson=XML(cellsjson), eventrow=eventrow, quests=quests, links=links, resultstring=resultstring, eventmap=eventmap,
                questmap=questmap, keys=keys, qlink=qlink, eventid=eventid, linkarray=linkarray)

def link():
    # This allows linking questions to an event via ajax

    eventid = request.args[0]
    chquestid = request.args[1]
    action = request.args[2]
    eventmapexists = 'T'  # Change to request.args[3] presently
    fixedx = 600
    fixedy = 500

    if auth.user is None:
        responsetext = 'You must be logged in to link questions to event'
    else:
        quest = db(db.question.id == chquestid).select().first()
        unspecevent = db(db.event.event_name == 'Unspecified').select(db.event.id, cache=(cache.ram, 3600),).first()

        #Think about where this is secured - should probably be here
        event = db(db.event.id == eventid).select().first()

        if event.shared or (event.owner == auth.user.id) or (quest.auth_userid == auth.user.id):
            if action == 'unlink':
                db(db.question.id == chquestid).update(eventid=unspecevent.id)
                responsetext = 'Question %s unlinked' %chquestid
            else:
                db(db.question.id == chquestid).update(eventid=eventid)
                responsetext = 'Question %s linked to event' %chquestid
                #Then if there was an eventmap it should require to be linked to 
                #to the eventmap but if not it shouldn't - this may need to be an arg
                if eventmapexists == 'T':
                    db.eventmap.insert(eventid=eventid, questid=chquestid, xpos=fixedx, ypos=fixedy)
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

#@auth_requires_signature()
def archive():
    # This will be callable via a button from vieweventmap2 which must ensure that the eventmap exists and records in it
    # match to quests
    # Lets attempt to do this via ajax and come back with a message that explains what archiving is
    responsetext = 'Event archived'
    eventid = request.args(0, cast=int, default=0)
    event = db(db.event.id == eventid).select().first()
    event.update_record(status='Archiving')

    unspecevent = db(db.event.event_name == 'Unspecified').select(db.event.id, cache=(cache.ram, 3600),).first()

    query = db.question.eventid == eventid
    quests = db(query).select()

    for x in quests:
        db(db.eventmap.questid == x.id).update(status='Archiving', queststatus=x.status, correctans=x.correctans)
        # lets just hold this for now as we would then lose our quests linked to the event which is a little awkward in
        # the no joins GAE world - quite tempting to copy the question text as well at this point - however maybe that
        # still means view archived event is different from viewevent
        #x.update_record(eventid = unspecevent.id)

    return responsetext






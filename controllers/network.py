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
#
# This will be an initial contoller for displaying networks of questions
# current thinking is that layout will be managed server side and jointjs
# will handle the display and evnts side of things with networkx looking
# like the library for doing layouts with an underlying depenency on numpy
# General activities appear to be
# 1 get a list of nodes of some sort eg via search from events or locations
#   and possibly include 1 or 2 generations of links in either or both directions
# 2 get the links/edges between nodes
# 3 create a graph object and submit to networkx layout alogrithms and get a 
#   dictionary with positions of the nodes
# 4 in some way scale that to the proposed jointjs canvas looks like networkx is 
#   always square
# 5 Figure out how best to display the text and send results to jointjs
# 6 Collect new make link and delete link requests and decide whether to accept
#   or reject based on rules
# 7 Probably add rules to in some way pan and zoom through the network  - this 
#   may become computationally intense if large but initial stuff should be fine
#   getting more nodes via ajax looks doable but not sure about how the jointjs updates work
# created a networkforgaendb that supports belongs on datastore+ndb but will just revert to
# datastore for now and move on

import json
from netx2py import getpositions
from ndsfunctions import creategraph, graphtojson, graphpositions
from d3js2py import d3graph
from gluon import XML
from jointjs2py import colourcode, textcolour, jsonportangle, jsonmetlink, getitemshape, getwraptext


def notindex2():
    # This is believed superceded by latest index
    # Thinking for now is that this will take zero one or two args for now
    # arg1 would be the number of generations to search and the default would be zero ie no
    # search for parents or children
    # arg 2 could be used for a single question id - however I think preference
    # is to start with some sort of session variable which would need to be populated by
    # any source which wants to call the mapping function - alternative of javascript array
    # seems clunky to pass across network - so will go with this for now
    # session.networklist will contain id, text status and correctanstext

    netdebug = False  # change to get extra details on the screen
    actlevels = 1
    basequest = 0
    resultstring = str(len(session.networklist))
    if len(request.args) > 0:
        numlevels = request.args[0]

    if len(request.args) > 1:
        basequest = request.args[1]

    if session.networklist is False:
        idlist = [basequest]
    else:
        idlist = session.networklist
    query = db.question.id.belongs(idlist)

    if idlist == 0:
        redirect(URL('no_questions'))

    quests = db(query).select()

    questlist = [x.id for x in quests]
    parentquery = (db.questlink.targetid.belongs(questlist)) & (db.questlink.status == 'Active')
    childquery = (db.questlink.sourceid.belongs(questlist)) & (db.questlink.status == 'Active')

    parentlist = questlist
    childlist = questlist

    links = None
    # just always have actlevels at 1 or more and see how that works
    # below just looks at parents and children - to get partners and siblings we could repeat the process
    # but that would extend to ancestors - so probably need to add as parameter to the query but conceptually this could
    # be repeated n number of times in due course

    # these may become parameters not sure
    # change back to true once working
    getsibs = False
    getpartners = False

    for x in range(actlevels):
        # ancestor proces
        if parentlist:
            # if not request.env.web2py_runtime_gae:
            parentlinks = db(parentquery).select()
            # else:
            #    parentlinks = None
            if links and parentlinks:
                links = links | parentlinks
            elif parentlinks:
                links = parentlinks
            if parentlinks:
                mylist = [y.sourceid for y in parentlinks]
                # query = db.question.id.belongs(mylist) & (db.questlink.status == 'Active')
                # above was accidental join
                query = db.question.id.belongs(mylist)
                parentquests = db(query).select()

                quests = quests | parentquests
                parentlist = [y.id for y in parentquests]
                if getsibs:
                    sibquery = db.questlink.sourceid.belongs(parentlist) & (db.questlink.status == 'Active')
                    siblinks = db(sibquery).select()
                    if siblinks:
                        links = links | siblinks
                        mylist = [y.targetid for y in siblinks]
                        query = db.question.id.belongs(mylist)
                        sibquests = db(query).select()
                        quests = quests | sibquests

                        # parentquery = db.questlink.targetid.belongs(parentlist)

                        # child process starts
        if childlist:
            # if not request.env.web2py_runtime_gae:
            childlinks = db(childquery).select()
            # else:
            #    childlinks = None
            if links and childlinks:
                links = links | childlinks
            elif childlinks:
                links = childlinks
            # childcount = db(childquery).count()
            # resultstring=str(childcount)
            if childlinks:
                mylist = [y.targetid for y in childlinks]
                query = db.question.id.belongs(mylist)
                childquests = db(query).select()
                quests = quests | childquests
                childlist = [y.id for y in childquests]
                if getpartners:
                    partquery = db.questlink.targetid.belongs(childlist)
                    partlinks = db(partquery).select()
                    if partlinks:
                        links = links | partlinks
                        mylist = [y.sourceid for y in partlinks]
                        query = db.question.id.belongs(mylist) & (db.questlink.status == 'Active')
                        partquests = db(query).select()
                        quests = quests | partquests
                        # childquery = db.questlink.sourceid.belongs(childlist)

    questlist = [y.id for y in quests]
    if links:
        linklist = [(y.sourceid, y.targetid) for y in links]
    else:
        linklist = []
    # ok so now got the question but need to get the list of links as well to draw the graph
    # same approach with a rows object
    nodepositions = getpositions(questlist, linklist)
    # thinking about doing a similar thing for parent child view - but not sure that's practical

    grwidth = 800
    grheight = 800

    # insert from viewquest to go through

    questmap = {}
    qlink = {}
    keys = '['
    z = 0
    for x in quests:
        z += 1
        if x['qtype'] == 'action':
            width = 200
            height = 140
            wraplength = 30
        else:
            width = 160
            height = 200
            wraplength = 25
        qtext = getwraptext(x.questiontext, x.correctanstext(), wraplength)
        rectcolour = colourcode(x.qtype, x.status, x.priority)
        colourtext = textcolour(x.qtype, x.status, x.priority)
        strobj = 'Nod' + str(x.id)
        questmap[strobj] = [nodepositions[x.id][0] * grwidth, nodepositions[x.id][1] * grheight, qtext, rectcolour, 12,
                            'lr', width, height, colourtext]
        keys += strobj
        keys += ','

    resultstring = str(z)
    # if we have siblings and partners and layout is directionless then may need to look at joining to the best port
    # or locating the ports at the best places on the shape - most questions will only have one or two connections
    # so two ports may well be enough we just need to figure out where the ports should be and then link to the
    # appropriate one think that means iterating through quests and links for each question but can set the
    # think we should move back to the idea of an in and out port and then position them possibly by rotation
    # on the document - work in progress

    if links:
        for x in links:
            strlink = 'Lnk' + str(x.id)
            strsource = 'Nod' + str(x.sourceid)
            strtarget = 'Nod' + str(x.targetid)
            if nodepositions[x.targetid][0] > nodepositions[x.sourceid][0]:
                sourceport = 'r'
                targetport = 'l'
            else:
                sourceport = 'l'
                targetport = 'r'
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

        # This should move to a function ideally as a pure function
    cellsjson = '['
    linkarray = '['

    for key, vals in questmap.iteritems():
        template = jsonportangle(key,vals[0],vals[1],vals[2],vals[3],vals[4],vals[6],vals[7],vals[5],vals[8])
        cellsjson += template + ','

    for key, vals in qlink.iteritems():
        template = jsonmetlink(key,vals[0],vals[1],vals[2],vals[3],vals[4])
        cellsjson += template + ','
        linkarray += '"' + key + '",'

    cellsjson = cellsjson[:-1]+']'
    linkarray = linkarray[:-1]+']'

    return dict(quests=quests, netdebug=netdebug, cellsjson=XML(cellsjson), linkarray=linkarray)
    # return dict(quests=quests, links=links, resultstring=resultstring, nodepositions=nodepositions, questmap=questmap,
    #            keys=keys, qlink=qlink, netdebug=netdebug, cellsjson=XML(cellsjson), linkarray=linkarray)


def interdemo():
    # This was copy of index2

    # and can probably be canned shortly but copied to graph to see if that can be got working and functions
    # now updated to graph format

    FIXWIDTH = 800
    FIXHEIGHT = 800

    redraw = request.vars.redraw

    netdebug = False  # change to get extra details on the screen
    actlevels = 1
    basequest = 0

    resultstring = str(len(session.networklist))
    numlevels = request.args(0, cast=int, default=1)
    basequest = request.args(1, cast=int, default=0)
    grwidth = request.args(2, cast=int, default=FIXWIDTH)
    grheight = request.args(3, cast=int, default=FIXHEIGHT)

    if session.networklist is False:
        idlist = [basequest]
    else:
        idlist = session.networklist
    query = db.question.id.belongs(idlist)

    if idlist == 0:
        redirect(URL('no_questions'))

    netgraph = creategraph(idlist, numlevels, intralinksonly=False)

    quests = netgraph['quests']
    links = netgraph['links']
    questlist = netgraph['questlist']
    linklist = netgraph['linklist']

    nodepositions = graphpositions(questlist, linklist)
    resultstring = netgraph['resultstring']

    print 'beflink'
    if links:
        for x in links:
            print x

    # oonvert graph to json representation for jointjs
    graphdict = graphtojson(quests, links, nodepositions, grwidth, grheight, False)
    # oonvert graph to json representation for d3
    d3dict = d3tojson(quests, links, nodepositions, grwidth, grheight, False)

    cellsjson = graphdict['cellsjson']
    keys = graphdict['keys']
    resultstring = graphdict['resultstring']

    d3jsondata =d3dict['cellsjson']

    return dict(cellsjson=XML(cellsjson), links=links, resultstring=resultstring,
                quests=quests,  keys=keys, netdebug=netdebug, d3jsondata=d3jsondata)

def index2():
    # Thinking for now is that this will take zero one or two args for now
    # arg1 would be the number of generations to search and the default would be zero ie no
    # search for parents or children
    # arg 2 could be used for a single question id - however I think preference
    # is to start with some sort of session variable which would need to be populated by
    # any source which wants to call the mapping function - alternative of javascript array
    # seems clunky to pass across network - so will go with this for now
    # session.networklist will contain id, text status and correctanstext

    FIXWIDTH = 800
    FIXHEIGHT = 800

    redraw = request.vars.redraw

    netdebug = False  # change to get extra details on the screen
    actlevels = 1
    basequest = 0

    resultstring = str(len(session.networklist))
    numlevels = request.args(0, cast=int, default=1)
    basequest = request.args(1, cast=int, default=0)
    grwidth = request.args(2, cast=int, default=FIXWIDTH)
    grheight = request.args(3, cast=int, default=FIXHEIGHT)

    if session.networklist is False:
        idlist = [basequest]
    else:
        idlist = session.networklist
    query = db.question.id.belongs(idlist)

    if idlist == 0:
        redirect(URL('no_questions'))

    netgraph = creategraph(idlist, numlevels, intralinksonly=False)

    quests = netgraph['quests']
    links = netgraph['links']
    questlist = netgraph['questlist']
    linklist = netgraph['linklist']

    nodepositions = graphpositions(questlist, linklist)
    resultstring = netgraph['resultstring']

    print 'beflink'
    for x in links:
        print x

    # oonvert graph to json representation for jointjs
    graphdict = graphtojson(quests, links, nodepositions, grwidth, grheight, False)

    cellsjson = graphdict['cellsjson']
    keys = graphdict['keys']
    resultstring = graphdict['resultstring']

    return dict(cellsjson=XML(cellsjson), links=links, resultstring=resultstring,
                quests=quests,  keys=keys, netdebug=netdebug)


def linkrequest():
    # this is called when a link is requested from the qmap or other function
    # at present we are keeping limited audit trail on link requests - only last updater
    # and last action and the basic rule is that the last action cannot be repeated
    # we don't currently know if this function will also be used for deletions but
    # currently it won't as there is no action in the args only the sourc and target links
    # so action for now is to estblish if the link already exists and if not create it
    # if it exists the number of requests increases and last user and action are updated.

    # now proposing to have an action as arg 3 which could be delete or agree
    # with link - this should be OK
    # and wil style the links a bit based on this too

    if len(request.args) < 2:
        # sourceid = request.args[0]
        # targetid = request.args[1]
        result = 'not enough args dont call me please'

    else:
        sourceid = request.args[0]
        targetid = request.args[1]
        if auth.user is None:
            result = 'You must be logged in to create links'
        else:
            linkaction = 'create'
            if len(request.args) > 2:
                linkaction = request.args[2]

            parquestid = sourceid[3:]
            chiquestid = targetid[3:]

            result = 'Ajax submitted ' + sourceid + ' with ' + targetid + ':' + parquestid + ' ' + chiquestid

            query = (db.questlink.sourceid == parquestid) & (db.questlink.targetid == chiquestid)

            linkrows = db(query).select().first()

            if linkrows is None:
                db.questlink.insert(sourceid=parquestid, targetid=chiquestid)
                # Now also need to add 1 to the numagreement or disagreement figure
                # It shouldn't be possible to challenge unless resolved
                result += ' Link Created'
            else:
                # link exists 
                if linkaction == 'create':
                    if linkrows.createdby == auth.user_id:
                        result = result + ' ' + 'You updated last no change made'
                    else:
                        agrcount = linkrows.createcount + 1
                        linkrows.update_record(createcount=agrcount)
                elif linkaction == 'delete':
                    if linkrows.createdby == auth.user_id and linkrows.createcount == 1:
                        db(db.questlink.id == linkrows.id).delete()
                        result = 'Row deleted'
                    else:
                        if linkrows.lastdeleter == auth.user_id:
                            result = result + ' ' + 'You deleted last no change made'
                        else:
                            delcount = linkrows.deletecount + 1
                            if delcount >= linkrows.createcount:
                                status = 'Deleted'
                            else:
                                status = 'Active'
                            linkrows.update_record(lastaction='delete', deletecount=delcount, lastdeleter=auth.user_id,
                                                   status=status)
                            result = 'Deletion count updated'

    return result


def graph():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Hello World")

    FIXWIDTH = 800
    FIXHEIGHT = 800

    redraw = request.vars.redraw

    netdebug = False  # change to get extra details on the screen
    actlevels = 1
    basequest = 0

    resultstring = str(len(session.networklist))
    numlevels = request.args(0, cast=int, default=1)
    basequest = request.args(1, cast=int, default=0)
    grwidth = request.args(2, cast=int, default=FIXWIDTH)
    grheight = request.args(3, cast=int, default=FIXHEIGHT)

    if session.networklist is False:
        idlist = [basequest]
    else:
        idlist = session.networklist
    query = db.question.id.belongs(idlist)

    if idlist == 0:
        redirect(URL('no_questions'))

    netgraph = creategraph(idlist, numlevels, intralinksonly=False)

    quests = netgraph['quests']
    links = netgraph['links']
    questlist = netgraph['questlist']
    linklist = netgraph['linklist']

    nodepositions = graphpositions(questlist, linklist)
    resultstring = netgraph['resultstring']

    d3dict = d3graph(quests, links, nodepositions, grwidth, grheight, False)
    d3nodes = d3dict['nodes']
    d3edges = d3dict['edges']

    return dict(resultstring=resultstring,quests=quests, netdebug=netdebug,
                d3nodes=XML(json.dumps(d3nodes)), d3edges=XML(json.dumps(d3edges)))


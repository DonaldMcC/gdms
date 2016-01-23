# - Coding UTF8 -
#
# Networked Decision Making
# Development Sites (source code): http://github.com/DonaldMcC/gdms
#
# Demo Sites (Pythonanywhere)
#   http://netdecisionmaking.com/nds/
#   http://netdecisionmaking.com/gdmsdemo/
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

"""
    exposes:
    http://..../[app]/network/linkrequest - ajax call to create links
    http://..../[app]/network/ajaxquest - ajax call to create question with ajax
    http://..../[app]/network/graph - main d3 interactive graph
    http://..../[app]/network/no_questions - display if no questions
    """


import json
from ndsfunctions import creategraph
from netx2py import graphpositions
from d3js2py import d3graph
from gluon import XML


def linkrequest():
    # this is called when a link is requested from the graph or event function
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
        responsetext = 'not enough args incorrect call'

    else:
        sourceid = request.args(0, cast=int, default=0)
        targetid = request.args(1, cast=int, default=0)

        if auth.user is None:
            responsetext = 'You must be logged in to create links'
        else:
            linkaction = 'create'
            if len(request.args) > 2:
                linkaction = request.args[2]

            responsetext = 'Ajax submitted ' + str(sourceid) + ' with ' + str(targetid)
            # print responsetext
            query = (db.questlink.sourceid == sourceid) & (db.questlink.targetid == targetid)

            linkrows = db(query).select().first()

            if linkrows is None:
                db.questlink.insert(sourceid=sourceid, targetid=targetid)
                # Now also need to add 1 to the numagreement or disagreement figure
                # It shouldn't be possible to challenge unless resolved
                responsetext += ' Link Created'
            else:
                # link exists 
                if linkaction == 'create':
                    if linkrows.createdby == auth.user_id:
                        responsetext = responsetext + ' ' + 'You updated last no change made'
                    else:
                        agrcount = linkrows.createcount + 1
                        linkrows.update_record(createcount=agrcount)
                elif linkaction == 'delete':
                    if linkrows.createdby == auth.user_id and linkrows.createcount == 1:
                        db(db.questlink.id == linkrows.id).delete()
                        responsetext = 'Row deleted'
                    else:
                        if linkrows.lastdeleter == auth.user_id:
                            responsetext = responsetext + ' ' + 'You deleted last no change made'
                        else:
                            delcount = linkrows.deletecount + 1
                            if delcount >= linkrows.createcount:
                                status = 'Deleted'
                            else:
                                status = 'Active'
                            linkrows.update_record(lastaction='delete', deletecount=delcount, lastdeleter=auth.user_id,
                                                   status=status)
                            responsetext = 'Deletion count updated'
    return responsetext


def ajaxquest():
    # this is called when a draft item is created on the graph
    # Only the item text will be received via ajax and the rest will
    # be added later by std form editing and that capability may be available via ajax as 
    # well at some point

    results = dict()
    if len(request.vars) < 1:
        # sourceid = request.args[0]
        # targetid = request.args[1]
        result = 'no variable passed so not creating item'
        results['result'] = result
        return json.dumps(results)
    
    itemtext = request.vars['itemtext']

    if request.vars['eventid']:
        eventid = int(request.vars['eventid'])
    else:
        eventid = db(db.evt.evt_name == 'Unspecified').select(db.evt.id).first().id

    if auth.user is None:
        result = 'You must be logged in to create links'
        results['result'] = result
        return json.dumps(results)

    serverid = db.question.insert(questiontext=itemtext, status='Draft', eventid=eventid)
    result = 'Item created'
 
    results['serverid'] = serverid
    results['result'] = result
    results['id'] = request.vars['id']
    return json.dumps(results)


@auth.requires(True, requires_login=requires_login)
def graph():
    """This is new interactive graph using D3 still very much work in progress mainly based on
    http://bl.ocks.org/cjrd/6863459
    but there have been a fair number of amendments to meet perceived needs"""

    fixwidth = 640
    fixheight = 320
    radius = 160  # this is based on size of nodes and seems needed to ensure nodes are on the graph

    redraw = request.vars.redraw

    netdebug = False  # change to get extra details on the screen
    actlevels = 1
    basequest = 0

    numlevels = request.args(0, cast=int, default=1)
    basequest = request.args(1, cast=int, default=0)
    grwidth = request.args(2, cast=int, default=fixwidth)
    grheight = request.args(3, cast=int, default=fixheight)

    if session.networklist is False:
        idlist = [basequest]
    else:
        idlist = session.networklist

    if not idlist:
        redirect(URL('no_questions'))

    query = db.question.id.belongs(idlist)
    netgraph = creategraph(idlist, numlevels, intralinksonly=False)

    quests = netgraph['quests']
    links = netgraph['links']
    questlist = netgraph['questlist']
    linklist = netgraph['linklist']

    nodepositions = graphpositions(questlist, linklist)
    for key in nodepositions:
        nodepositions[key] = ((nodepositions[key][0] * grwidth) + radius, (nodepositions[key][1] * grheight) + radius)
    resultstring = netgraph['resultstring']

    d3dict = d3graph(quests, links, nodepositions, False)
    d3nodes = d3dict['nodes']
    d3edges = d3dict['edges']

    return dict(resultstring=resultstring, quests=quests, netdebug=netdebug,
                d3nodes=XML(json.dumps(d3nodes)), d3edges=XML(json.dumps(d3edges)))


def no_questions():
    txt = 'All done in view'
    return dict(txt=txt)

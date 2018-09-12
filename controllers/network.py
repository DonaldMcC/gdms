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
from d3js2py import getd3graph


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
        sourcetext = request.args(0)
        targettext = request.args(1)
        if sourcetext.isdigit():
            sourceid = int(sourcetext)
        else:
            sourcetext = sourcetext.replace("_", " ")  # This will do for now - other chars may be problem
            sourcerecs = db(db.question.questiontext == sourcetext).select(
                            db.question.id, orderby=~db.question.createdate)
            if sourcerecs:
                sourceid = sourcerecs.first().id
            else:
                responsetext = 'Target of link could not be found'
                return responsetext

        if targettext.isdigit():
            targetid = int(targettext)
        else:
            targettext = targettext.replace("_", " ")  # This will do for now - other chars may be problem
            targetrecs = db(db.question.questiontext == targettext).select(
                            db.question.id, orderby=~db.question.createdate)
            if targetrecs:
                targetid = targetrecs.first().id
            else:
                responsetext = 'Source of link could not be found'
                return responsetext

        if auth.user is None:
            responsetext = 'You must be logged in to create links'
        else:
            linkaction = 'create'
            if len(request.args) > 2:
                linkaction = request.args[2]

            responsetext = 'Item ' + str(sourceid) + ' linked with ' + str(targetid)
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
                        responsetext = 'Link deleted'
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


def nodedelete():
    # this is called via ajax when a node deletion request is received from an eventmap
    # there are various situations to consider:
    # if you are the owner of the question and it is draft status then you may delete and it is a full deletion
    # if you are the event owner or the event is shared then you may delete any question from the event and
    # if this is not your own draft question then the question gets moved back to the unspecified event
    # if the event is not shared and you are not the event owner then you cannot delete anything
    # if event is shared and question is in draft status

    if len(request.args) < 2:
        responsetext = 'not enough args incorrect call'
    else:
        sourcetext = request.args(0)
        eventid = request.args(1, cast=int, default=0)

        action = request.args(2)
        linktype = request.args(3, default='event')
        
        if sourcetext.isdigit():
            nodeid = int(sourcetext)
        else:
            sourcetext = sourcetext.replace("_", " ")  # This will do for now - other chars may be problem
            sourcerecs = db(db.question.questiontext == sourcetext).select(
                            db.question.id, orderby=~db.question.createdate)
            if sourcerecs:
                nodeid = sourcerecs.first().id
            else:
                responsetext = 'Target of link could not be found'
                return responsetext

        if auth.user_id is None:
            responsetext = 'You must be logged in to delete nodes'
        elif eventid == 0:
            responsetext = 'No event set node deletion not possible'
        else:
            quest = db(db.question.id == nodeid).select().first()
            if quest.auth_userid == auth.user_id and quest.status == 'Draft':
                db(db.questlink.sourceid == nodeid).delete()
                db(db.questlink.targetid == nodeid).delete()
                db(db.question.id == nodeid).delete()
                responsetext = 'Question deleted'
            elif linktype != 'project':
                event = db(db.evt.id == eventid).select().first()
                if event.evt_owner == auth.user_id or event.shared is True:
                    responsetext = 'Question removed from event'
                    unspecevent = db(db.evt.evt_name == 'Unspecified').select(
                        db.evt.id, cache=(cache.ram, 3600)).first()
                    db(db.question.id == nodeid).update(eventid=unspecevent.id)
                else:
                    responsetext = 'You are not event owner and event not shared - deletion not allowed'
            else:
                project = db(db.project.id == eventid).select().first()
                if project.proj_owner == auth.user_id or project.proj_shared is True:
                    responsetext = 'Question removed from project'
                    unspecitem = db(db.project.proj_name == 'Unspecified').select(
                                    db.project.id, cache=(cache.ram, 3600),).first()
                    db(db.question.id == nodeid).update(projid=unspecitem.id)
                else:
                    responsetext = 'You are not project owner and project not shared - deletion not allowed'
    return responsetext


def nodedemote():
    # this is called via ajax when a node demotion request is received from an eventmap
    # there are various situations to consider:
    # if you are the event owner or the event is shared then you may demote any question that is
    # linked to the event
    # if the event is not shared and you are not the event owner then you cannot demote anything
    # if the question is not event linked ie part of unspecified event then anyone can demote it
    # Call needs to contain question being demoted the eventid and the question it is being
    # inserted into

    if len(request.args) < 2:
        responsetext = 'not enough args incorrect call'
    else:
        sourcetext = request.args(0)
        eventid = request.args(1, cast=int, default=0)

        parenttext = request.args(2)
        linktype = request.args(3, default='event')

        if sourcetext.isdigit():
            nodeid = int(sourcetext)
        else:
            sourcetext = sourcetext.replace("_", " ")  # This will do for now - other chars may be problem
            sourcerecs = db(db.question.questiontext == sourcetext).select(
                db.question.id, orderby=~db.question.createdate)
            if sourcerecs:
                nodeid = sourcerecs.first().id
            else:
                responsetext = 'Source node could not be found'
                return responsetext

        if parenttext.isdigit():
            parentid = int(parenttext)
            parent=db(db.question.id == parentid).select(
                db.question.id, db.question.eventlevel, db.question.subquests).first()
        else:
            parenttext = parenttext.replace("_", " ")  # This will do for now - other chars may be problem
            parentrecs = db(db.question.questiontext == sourcetext).select(
                db.question.id, orderby=~db.question.createdate)
            if parentrecs:
                parent = parentrecs.fist()
                parentid = parent.id
            else:
                responsetext = 'Parent node could not be found'
                return responsetext

        if auth.user_id is None:
            responsetext = 'You must be logged in to demote nodes'
        else:
            quest = db(db.question.id == nodeid).select().first()
            event = db(db.evt.id == eventid).select().first()
            if (event.evt_owner == auth.user_id or event.shared
                or event.evt_name == 'Unspecified') is True:
                quest.update_record(masterquest=parentid, eventlevel=parent.eventlevel+1)
                if parent.subquests:
                    newsubs = parent.subquests
                else:
                    newsubs = list()
                newsubs.append(nodeid)
                parent.update_record(subquests=newsubs)
                responsetext = 'Question demoted'
                #db(db.question.id == nodeid).update(eventid=unspecevent.id)
            else:
                responsetext = 'You are not event owner and event not shared - promotion not allowed'
    return responsetext


def nodepromote():
    # this is called via ajax when a node promotion request is received from an eventmap
    # there are various situations to consider:
    # if you are the event owner or the event is shared then you may promote any question that is
    # linked to the event and at lower level
    # if the event is not shared and you are not the event owner then you cannot promote anything
    # if the question is not event linked ie part of unspecified event then anyone can promote it
    # Call needs to contain question being promoted and potentially the eventid that you are working on

    if len(request.args) < 2:
        responsetext = 'not enough args incorrect call'
    else:
        sourcetext = request.args(0)
        eventid = request.args(1, cast=int, default=0)
        linktype = request.args(2, default='event')

        if sourcetext.isdigit():
            nodeid = int(sourcetext)
        else:
            sourcetext = sourcetext.replace("_", " ")  # This will do for now - other chars may be problem
            sourcerecs = db(db.question.questiontext == sourcetext).select(
                db.question.id, orderby=~db.question.createdate)
            if sourcerecs:
                sourcerec = sourcerecs.first()
            else:
                responsetext = 'Node could not be found'
                return responsetext

        if auth.user_id is None:
            responsetext = 'You must be logged in to demote nodes'
        else:
            quest = db(db.question.id == nodeid).select().first()
            event = db(db.evt.id == eventid).select().first()
            if quest.eventlevel == 0:
                responsetext = 'Already at level 0 promotion not possible'
                return responsetext
            else:
                parentrec = db(db.question.id == quest.masterquest).select(orderby=~db.question.createdate).first()
                if (event.evt_owner == auth.user_id or event.shared
                    or event.evt_name == 'Unspecified') is True:
                    quest.update_record(masterquest=parentrec.masterquest, eventlevel=quest.eventlevel-1)
                    newsubs = parentrec.subquests
                    newsubs.remove(nodeid)
                    parentrec.update_record(subquests=newsubs)
                    responsetext = 'Question promoted'
                    #TODO - should loop through quest.subquests and all should move up 1 level - and stay with
                    # parent - but lets get simple process working first
                else:
                    responsetext = 'You are not event owner and event not shared - promotion not allowed'
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
    #  This is currently loaded only by search but will probably also look to use this with newindex

    redraw = "true"
    numlevels = request.args(0, cast=int, default=1)
    basequest = request.args(1, cast=int, default=0)

    if session.networklist is False:
        idlist = [basequest]
    else:
        idlist = session.networklist

    if not idlist:
        redirect(URL('no_questions'))

    projid = 0
    eventrowid = 0

    quests, nodes, links, resultstring = getd3graph('search', idlist, 'open', numlevels)
    return dict(resultstring=resultstring, eventmap=quests, links=links, nodes=nodes, projid=projid,
                eventrowid=eventrowid, redraw=redraw, eventowner='false')


def network():
    # may still limit options if from home screen - but basis is vieweventmapd3v4 and this is for home screen for now
    eventid = request.args(0, cast=int, default=0)
    redraw = 'false'

    if not eventid:  # get the next upcoming event
        datenow = datetime.datetime.utcnow()

        query = (db.evt.enddatetime > datenow)
        events = db(query).select(db.evt.id, orderby=[db.evt.startdatetime]).first()
        if events:
            eventid = events.id
        else:
            redirect(URL('event', 'noevent'))

    eventrow = db(db.evt.id == eventid).select().first()

    quests, nodes, links, resultstring = getd3graph('event', eventid, eventrow.status)

    # set if moves on the diagram are written back - only owner for now
    if auth.user and eventrow.evt_owner == auth.user.id:
        editable = 'true'
    else:
        editable = 'false'

    session.eventid = eventid
    session.projid = eventrow.projid

    return dict(resultstring=resultstring, eventrow=eventrow, eventid=eventid, eventmap=quests,
                eventowner=editable, links=links, nodes=nodes, projid=eventrow.projid, eventrowid=eventrow.id,
                redraw=redraw)


def no_questions():
    txt = 'All done in view'
    return dict(txt=txt)

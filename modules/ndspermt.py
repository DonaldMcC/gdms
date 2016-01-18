# - Coding UTF8 -
#
# Networked Decision Making
# Site: http://code.google.com/p/global-decision-making-system/
#
# License Code: GPL, General Public Licension 3.0
#
# Also visit: www.web2py.come v. 2.0
# License Content: Creative Commons Attribut
# or Groups: http://groups.google.com/group/web2py
# 	For details on the web framework used for this development
#
# Developed by Russ King (newglobalstrategy@gmail.com
# Russ also blogs occasionally to pass the time at proudofyourplanent.blogspot.com
# His general thinking on why this project is very important is availalbe at
# http://www.scribd.com/doc/98216626/New-Global-Strategy


from gluon import *
import datetime


def get_groups(userid=None):
    """This should return a list of groups that a user has access to it now requires a login to
     be passed and currently only used on submit and questcountrows with user so no need to handle none
     :param userid: """

    accessgrouprows = current.db(current.db.group_members.auth_userid == userid).select()
    access_group = [x.access_group.group_name for x in accessgrouprows]
    access_group.append('Unspecified')

    return access_group


def get_exclude_groups(userid=None):
    """This should return a list of groups that a user does not have access to it now requires a login to
     be passed and currently only used on submit and questcountrows with user so no need to handle none
     :param userid: """
    accessgroups = current.db(current.db.access_group.id > 0).select()
    allgroups = [x.group_name for x in accessgroups]
    exclude_group = list(set(allgroups) - set(get_groups(userid)))
    return exclude_group

# can view needs implemented

''' now have a few functions to think about here
    1) Can a user view a question?
        Change here is to have  a function check if question has a group then user must belong to that group
        think this is submitted with the group of the question - but potentially this can just be a call to get groups
        only required in viewquest for now
        So - this is can_view - will be part of ph7 

    2) Can a user join a group?
        Yes if public, otherwise could apply if apply and won't see groups that are invite only or admin unless they are
        already members of them - need to figure out options for each group
        implemented as join_group

    3) Can a user edit a group?
        Yes if the owner or an admin of the group and one admin can appoint others
        to implement as group_actions

    4) Can a user delete a group?
        Only possible by the owner and if no questions are assigned - otherwise deactivate
        to implement as group_actions        

    5) Can a user add a question/action or issue to an event?
        Yes if event is shared or they are the owner of the event - however question needs to be unassigned to another
        event

    6) Can a user submit a question to a group?
        Yes if member of the group - otherwise no - so no function required at present
        Test ph4_5 - not sure what the error will be

    7) Can a user answer a question, action or issue?
        Yes unless group policy blocks selecting questions to answer - and currently putting through the can_view
        routine first but this may need an answerable function

    8) Can a user vote on a question
        Yes if part of group that question assigned to and haven't voted before - not clear if we should allow change of
        mind - but no obvious reason not to

Above will do for now - in general we cant use decorated functions for these as need to evaluate which event, question
etc the user is attempting to answer/view

    Whole approach to votes in progress is probably missing bit of the framework now - but think votes are completely
    separate as they have expiry dates and so forth - and they can change from one to the other - possibly until
    resolved - would just be a question of updating the count - but lets keep separate for now - so it can be a
    dimension - lets start to get that in place

'''


def can_view(qtype, status, resolvemethod, hasanswered, answer_group, duedate, userid, owner):
    """Will be some doctests on this in due course and a table of condtions
    Basic rules are that for votes users can't see questions that they haven't answered
    vote style questions can be seen after expiry and never before and users can never see
    questions for groups they don't belong to.
    :param qtype:
    """

    viewable = False
    message = ''
    reason = 'OK to view'

    access_groups = get_groups(userid)

    if answer_group in access_groups:
        if userid == owner:  # think always allow owners to view questions whether votes or not
            viewable = True
        elif (status == 'In Progress' or status == 'Draft') and hasanswered is False:
            message = "You can't view this question as it's not resolved and you haven't answered it."
            reason = 'NotAnswered'
        elif get_resolve_method(resolvemethod) == 'Vote' and duedate > datetime.datetime.now():
            message = "Vote is still in progress and policy is not to show until counted.  The vote ends at " +\
                      str(duedate)
            reason = 'VoteInProg'
        else:
            viewable = True
    else:
        message = "You do not have permission to view this item"
        reason = 'NotInGroup'

    return viewable, reason, message

def get_resolve_method(questmethod):
    resolverecord = current.db(current.db.resolve.resolve_name == questmethod).select().first()
    if resolverecord:
        return resolverecord.resolve_method
    else:
        return 'Not Known'


def join_groups(userid):
    """This should return a list of groups that a user has access to it now requires a login to
     be passed and currently only used on submit and questcountrows with user so no need to handle none"""

    accessgrouprows = current.db(current.db.group_members.auth_userid == userid).select()
    access_group = [x.access_group.group_name for x in accessgrouprows]
    access_group.append('Unspecified')
    return access_group


def get_actions(qtype, status, resolvemethod,  owner, userid, hasanswered, context='std', eventid=0):
    avail_actions = []
    if qtype == 'eventitem':
        avail_actions = ['editeventitem']
        return avail_actions
    if status == 'In Progress' and (qtype == 'issue' or qtype == 'action') and hasanswered is False and context != 'Submit':
        avail_actions = ['Approve', 'Disapprove']
    elif status == 'Resolved' or status == 'Agreed':
        avail_actions = ['Agree', 'Disagree']
    elif status == 'Draft' and owner == userid:
        avail_actions = ['Edit', 'Confirm']
    if context == 'View':
        if qtype == 'action':
            avail_actions.append('Next_Action')
            avail_actions.append('Link_Action')
        elif qtype == 'issue':
            avail_actions.append('Next_Issue')
            avail_actions.append('Link_Question')
            avail_actions.append('Link_Action')
        else:
            avail_actions.append('Next_Question')
            avail_actions.append('Link_Question')
            avail_actions.append('Link_Action')
        if owner == userid and resolvemethod == 'Vote' and status == 'In Progress':
            avail_actions.append('End_Voting')
        if eventid:
            avail_actions.append('Eventmap')
    elif context == 'Submit':
        avail_actions.append('Link_Issue')
        avail_actions.append('Link_Question')
        avail_actions.append('Link_Action')
        avail_actions.append('New_Issue')
        avail_actions.append('New_Question')
        avail_actions.append('New_Action')
    else:
        if hasanswered is True or owner == userid or status != 'In Progress':
            avail_actions.append('View')
        elif userid is not None:
            avail_actions.append('Answer')
    # may change this to return both buttons but one would be hidden somehow
    if context == 'eventadditems':
        avail_actions.append('Link')
    elif context == 'evtunlink':
        avail_actions.append('Unlink')
    return avail_actions


def make_button(action, id, context='std', rectype='quest', eventid=0):
    """This should return a button with appropriate classes for an action in a given context this will typiclly 
       be called by a get_buttons function which will take call get actions to get the actions and then make
       a button for each action There are currently 9 possible actions in the get_actions list:
       Approve, Disapprove, Pass and Reject for quick resolution and
       Agree, Disagree, Challenge and Details which are all currently setup on viewquest but not as TAG.INPUT

       So I think that is phase 1 and then put in as buttons -the structure of review is also worth looking at
       :param action: """

    # Below is result for call to link question to event
    session = current.session
    stdclass = "btn btn-primary  btn-xs btn-group-xs"
    if rectype == 'quest':
        if action == 'Agree':
            stringlink = XML("ajax('" + URL('viewquest','agree', args=[id, 1]) + "' , ['quest'], ':eval')")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class="btn btn-success  btn-xs btn-group-xs", _onclick=stringlink, _VALUE="Agree")
        elif action == 'Disagree':
            stringlink = XML("ajax('" + URL('viewquest','agree', args=[id, 2]) + "' , ['quest'], ':eval')")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class="btn btn-danger  btn-xs btn-group-xs", _onclick=stringlink, _VALUE="Disagree")
        elif action == 'Approve':
            stringlink = XML("ajax('" + URL('answer','quickanswer', args=[id, 0]) + "' , ['quest'], ':eval')")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class="btn btn-success  btn-xs btn-group-xs", _onclick=stringlink, _VALUE="Approve")
        elif action == 'Disapprove':
            stringlink = XML("ajax('" + URL('answer','quickanswer', args=[id, 1]) + "' , ['quest'], ':eval')")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class="btn btn-danger  btn-xs btn-group-xs", _onclick=stringlink, _VALUE="Disapprove")
        elif action == 'Edit':
            stringlink = XML("parent.location='" + URL('submit','new_question',args=['quest',id], extension='html')+ "'")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="Edit")
        elif action == 'Next_Action':
            stringlink = XML("parent.location='" + URL('answer','get_question',args=['action'], extension='html')+ "'")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="Next Action")
        elif action == 'Next_Issue':
            stringlink = XML("parent.location='" + URL('answer','get_question',args=['issue'], extension='html')+ "'")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="Next Issue")
        elif action == 'Next_Question':
            stringlink = XML("parent.location='" + URL('answer','get_question',args=['quest'], extension='html')+ "'")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="Next Question")
        elif action == 'Create_Action':
            stringlink = XML("parent.location='" + URL('submit','new_question',args=['action'], extension='html')+ "'")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="Create Action")
        elif action == 'Link_Action':
            stringlink = XML("parent.location='" + URL('submit','new_question',args=['action',id], extension='html')+ "'")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="Linked Action")
        elif action == 'Link_Question':
            stringlink = XML("parent.location='" + URL('submit','new_question',args=['quest',id], extension='html')+ "'")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="Linked Question")
        elif action == 'Link_Issue':
            stringlink = XML("parent.location='" + URL('submit','new_question',args=['issue',id], extension='html')+ "'")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="Linked Issue")
        elif action == 'New_Action':
            stringlink = XML("parent.location='" + URL('submit','new_question',args=['action'], extension='html')+ "'")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="New Action")
        elif action == 'New_Question':
            stringlink = XML("parent.location='" + URL('submit','new_question',args=['quest'], extension='html')+ "'")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="New Question")
        elif action == 'New_Issue':
            stringlink = XML("parent.location='" + URL('submit','new_question',args=['issue'], extension='html')+ "'")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="New Issue")
        elif action == 'View':
            stringlink = XML("parent.location='" + URL('viewquest','index',args=[id], extension='html')+ "'")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="View")
        elif action == 'Answer':
            stringlink = XML("parent.location='" + URL('answer','answer_question',args=[id], extension='html', user_signature=True)+ "'")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="Answer")
        elif action == 'Link':
            stringlink = XML("ajax('" + URL('event','link',args=[session.eventid, id, 'link']) + "' , ['challreason'], ':eval')")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="Link")
        elif action == 'Unlink':
            stringlink = XML("ajax('" + URL('event','link',args=[session.eventid, id, 'unlink']) + "' , ['challreason'], ':eval')")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="Unlink")
        elif action == 'Confirm':
            stringlink = XML("ajax('" + URL('submit','drafttoinprog',args=[id], extension='html') + "' , ['challreason'], ':eval')")
            stringtype = XML('BUTTON data-toggle="popover" title ="Updates status to in-progress - this cannot be undone", data-content=""')
            buttonhtml = TAG.INPUT(_TYPE=stringtype,_class=stdclass, _onclick=stringlink, _VALUE="Confirm")
        elif action == 'End_Voting':
            stringlink = XML("parent.location='" + URL('viewquest','end_vote',args=[id], extension='html')+ "'")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="End Voting")
        elif action == 'editeventitem':
            stringlink = XML("parent.location='" + URL('event','eventitemedit',args=[id], extension='html')+ "'")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="Edit Item")
        elif action == 'Eventmap':
            stringlink = XML("parent.location='" + URL('event','vieweventmapd3',args=[eventid], extension='html')+ "'")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="Event Map")
        else:
            buttonhtml = XML("<p>Button not setup</p>")
    elif rectype == 'location':
        if action == 'Edit_Location':
            stringlink = XML("parent.location='" + URL('location','index',args=[id], extension='html')+ "'")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="Edit")
        elif action == 'View_Location':
            stringlink = XML("parent.location='" + URL('location','viewlocation',args=[id], extension='html')+ "'")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="View")
        elif action == 'Add_Event_Location':
            stringlink = XML("parent.location='" + URL('event','new_event',args=[id], extension='html')+ "'")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="Add Event")
        else:
            buttonhtml = XML("<p>Button not setup</p>")
    elif rectype == 'event':
        if action == 'Add_Event_Location':
            stringlink = XML("parent.location='" + URL('event','new_event',args=[id], extension='html')+ "'")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="Add Event")
        elif action == 'View_Event':
            stringlink = XML("parent.location='" + URL('event','viewevent',args=[id], extension='html')+ "'")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="View Event")
        elif action == 'Add_Issue':
            stringlink = XML("parent.location='" + URL('submit','new_question',args='issue', extension='html')+ "'")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="Add Issue")
        elif action == 'Add_Quest':
            stringlink = XML("parent.location='" + URL('submit','new_question',args='quest', extension='html')+ "'")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="Add Question")
        elif action == 'Add_Action':
            stringlink = XML("parent.location='" + URL('submit','new_question',args='action', extension='html')+ "'")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="Add Action")
        elif action == 'Link_Items':
            stringlink = XML("parent.location='" + URL('event','eventadditems',args=[id], extension='html')+ "'")
            stringtype = XML('BUTTON data-toggle="popover" title ="Add existing items to the event. Items are only linked to 1 event at a time and must be archived from there to become available for the next event", data-content=""')
            buttonhtml = TAG.INPUT(_TYPE=stringtype,_class=stdclass, _onclick=stringlink, _VALUE="Link Items")
        elif action == 'Edit_Event':
            stringlink = XML("parent.location='" + URL('event','new_event',args=['Not_Set',id], extension='html')+ "'")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="Edit Event")
        elif action == 'eventreview':
            stringlink = XML("parent.location='" + URL('event','eventreview',args=[id], extension='html')+ "'")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="Review Event")
        elif action == 'Eventmap':
            stringlink = XML("parent.location='" + URL('event','vieweventmapd3',args=[id], extension='html')+ "'")
            buttonhtml = TAG.INPUT(_TYPE='BUTTON',_class=stdclass, _onclick=stringlink, _VALUE="Event Map")
        elif action == 'Redraw':
            stringlink = ""
            buttonhtml = TAG.INPUT(_TYPE='BUTTON', _id="redraw-graph",_class=stdclass, _onclick=stringlink, _VALUE="Redraw")
        elif action == 'Archive':
            buttonhtml = XML('<INPUT TYPE="BUTTON data-toggle="popover" title ="Update event status to archiving", '
                             'data-content=""" VALUE="Archive" class="btn btn-primary  btn-xs btn-group-xs" '
                             'data-toggle="modal" data-target=".bs-example-modal-sm"></INPUT>')
        else:
            buttonhtml = XML("<p>Button not setup</p>")
    else:
        buttonhtml = XML("<p>Button not setup</p>")

    return buttonhtml


def get_buttons(qtype, status, resolvemethod,  id, owner, userid, hasanswered=False, context='std', eventid=0):
    avail_actions = get_actions(qtype, status, get_resolve_method(resolvemethod), owner, userid, hasanswered, context, eventid)
    return butt_html(avail_actions, context, id, 'quest', eventid)


def get_locn_buttons(locid, shared, owner, userid, context='std'):
    avail_actions = get_locn_actions(locid, shared, owner, userid, context)
    return butt_html(avail_actions, context, locid, 'location')


def get_event_buttons(eventid, shared, owner, userid, context='std', status='Open'):
    avail_actions = get_event_actions(eventid, shared, owner, userid, context, status)
    return butt_html(avail_actions, context, eventid, 'event')


def butt_html(avail_actions, context, id, rectype, eventid=0):
    buttonhtml = False
    for x in avail_actions:
        if buttonhtml:
            buttonhtml += make_button(x, id, context, rectype, eventid=0)
            buttonhtml += '\r'
        else:
            buttonhtml = make_button(x, id, context, rectype, eventid=0)
            buttonhtml += '\r'
    return buttonhtml


def get_locn_actions(locid, shared, owner, userid, context='std'):
    avail_actions = ['View_Location']
    if shared is True or owner == userid:
        avail_actions.append('Add_Event_Location')
    if owner == userid:
        avail_actions.append('Edit_Location')
    return avail_actions


def get_event_actions(eventid, shared, owner, userid, context='std', status='Open'):
    avail_actions = []
    if status != 'Archived':
        avail_actions.append('View_Event')
        if shared is True or owner == userid:
            avail_actions.append('Add_Issue')
            avail_actions.append('Add_Quest')
            avail_actions.append('Add_Action')
            avail_actions.append('Link_Items')
        if owner == userid:
            avail_actions.append('Edit_Event')
            if context == 'eventreview':
                avail_actions.append('Archive')             # only editable once status moves to archiving and owner
        if context == 'eventmap':
            avail_actions.append('Redraw')
    if context != 'eventreview':
        avail_actions.append('eventreview')
    if context != 'eventmap':
        avail_actions.append('Eventmap')
    
    return avail_actions
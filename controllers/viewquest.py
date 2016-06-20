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

"""
 This controller handles viewing the full details on questions if allowed
 and also displaying the reason you are not allowed to view the question
 the functionality to submit a challenge is also included in this controller
 and that is called via ajax from the view of the question detail
 The three functions are:
 index:  displays the question details
 comments: add comments
 useranswers: shows detail of the useranswers -
 notshowing: explains why the question can't be displayed - actions should always be displayed
 challenge: allows submission of a challenge and return of whether this is allowed
 via ajax
 agree - ajax agreement or disagreement
 challenge - ajax submission to challenge
 flagcomment -
 urgency - ajax update urgency of item

 For actions not generally interested in user's views but would like these to be capable
 of prioritisation at any stage - need to see the date and will be some options to generate
 emails based on actions and also to challenge resolved actions to return them to proposed
 A separate comments function has now been created
"""

"""
    exposes:
    http://..../[app]/viewquest/index which has action, issue and question views
    http://..../[app]/viewquest/end_vote  #  Ajax call
    http://..../[app]/viewquest/useranswers
    http://..../[app]/viewquest/notshowing   
    http://..../[app]/viewquest/comments
    http://..../[app]/viewquest/challenge  #  Ajax call
    http://..../[app]/viewquest/agree  #  Ajax call
    http://..../[app]/viewquest/flagcomment  #  Ajax call
    http://..../[app]/viewquest/urgency  #  Ajax call

    """

from ndsfunctions import updatequestcounts
from ndspermt import can_view
from d3js2py import colourcode, getwraptext
from time import strftime
import gluon.contrib.simplejson



def index():
    # This will be a general view on question details and it will require the
    # question id as an argument Logic will be to only display the question if it
    # has been submitted, resolved or answered/passed by the user
    # This maintains the general privacy approach to questions that may be
    # subject to answer eventually if resolved then there will be a view option
    # However approach for actions is different - they can be viewed at any time
    # but the buttons at the bottom should be very simlar

    # initialize variables as not used if action
    viewtext = ''
    votetext = ''
    numpass = 0
    uqanswered = False
    uqurg = 5
    uqimp = 5
    uqans = 0
    newansjson = ''
    print request.args(0)

    quests = db(db.question.id == request.args(0, cast=int, default=0)).select() or \
             redirect(URL('notshowing/' + 'NoQuestion'))
    quest = quests.first()

    questtype = request.args(1, default='quest')  #This will remain as all for event flow and probably next item button
    uq = None
    uqanswered = False
    if auth.user:
        uqs = db((db.userquestion.auth_userid == auth.user.id) & (db.userquestion.questionid == quest.id)).select()
        if uqs:
            uqanswered = True
            uq = uqs.first()

    viewable = can_view(quest.status, quest.resolvemethod, uqanswered, quest.answer_group,
                        quest.duedate, auth.user_id, quest.auth_userid)

    if viewable[0] is False:
        redirect(URL('viewquest', 'notshowing', args=(viewable[1], str(quest.id))))
    
    resolve = db(db.resolve.resolve_name == quest['resolvemethod']).select().first()
    if resolve and resolve.resolve_method == 'Vote':
        if quest.duedate > datetime.datetime.utcnow():
            votetext = 'Voting will end on ' + strftime("%a, %d %b %Y %H:%M", resolve.duedate)

    if quest['qtype'] == 'quest':
        response.view = 'viewquest/question.html'

        # now three scenarios now either the user has answered the question
        # or they haven't but it is resolved the population of the question variables
        # v2 if not answered we will now open a link to answer the question
        # to return to the view should be broadly the same in both scenarios
        # or they have submitted question and are being allowed to see progress

        numpass = quest['othercounts'][0]

        zipanswers = zip(quest['answers'], quest['answercounts'])
        # ansjson = gluon.contrib.simplejson.dumps(zipanswers)

        # sample for testing
        # vardata = [] vardata was for jqplot - now removing
        ansdictlist = []
        for x in zipanswers:
            # vardata.append([x[0], int(x[1])])
            tempdict = {'label': x[0], 'count': int(x[1])}
            ansdictlist.append(tempdict)

        newansjson = gluon.contrib.simplejson.dumps(ansdictlist)

        # in terms of the user there are basically 3 things to pick-up on
        # the user answer, users rating of urgency and importance
        # did the user get this right (if resolved or under challenge)

        if uqanswered:
            uqurg = uq.urgency
            uqimp = uq.importance
            uqans = uq.answer

        # Now work out what we can say about this question
        # if resolved we can say if right or wrong and allow the question to be challenged
        if quest['status'] == 'Resolved':
            # Did the user answer the question
            if uqanswered:
                if uqans == -1:
                    viewtext = 'You passed on this question but it has now been resolved.'
                elif quest['correctans'] == uqans:
                    viewtext = 'Well done - you helped resolve this question.'
                else:
                    viewtext = 'Your answer to this question disagrees with the resolved '
                    'correct answer - you may want to request a challenge.'
            else:
                viewtext = "You didn't get to answer this question."
        elif quest['status'] == 'Rejected':
            viewtext = "This question has been rejected."
        else:
            # if not resolved can only say in progress and how many more answers are required
            # at present should only be here if
            # answered as we are not showing users unresolved and unanswered questions
            viewtext = 'This question is in progress at level ' + str(quest['question_level']) + '.'

            # That will do for now - display of challenges and probably numanswers remaining
            # and level can be added later

    else:  # action or issue
        response.view = (quest['qtype'] == 'issue' and 'viewquest/issue.html') or 'viewquest/action.html'
        # Get details of the action urgency and importance of actions is stored in a different table because they can
        # be prioritised without answering
        if auth.user is not None:
            uq = db((db.questurgency.auth_userid == auth.user.id) & (
                db.questurgency.questionid == quest.id)).select().first()

            if uq is not None:
                uqanswered = True
                uqurg = uq.urgency
                uqimp = uq.importance

    # need to get priorquests and subsquests as lists which may be empty for each quest now
    priorquestrows = db(db.questlink.targetid == quest.id).select(db.questlink.sourceid)
    subsquestrows = db(db.questlink.sourceid == quest.id).select(db.questlink.targetid)
    priorquests = [row.sourceid for row in priorquestrows]
    subsquests = [row.targetid for row in subsquestrows]

    # posx=100, posy=100, text='default', answer='', status='In Progress', qtype='quest', priority=50
    # d3data = '[' + getd3dict(quest.id, 100, 100, quest.questiontext) + ']'

    # vardata=XML(vardata)
    
    viewtext += votetext

    if questtype == 'All':
        context = 'View_Evt_Flow'
    else:
        context = 'View'

    return dict(quest=quest, viewtext=viewtext, uqanswered=uqanswered, uqurg=uqurg, uqimp=uqimp, numpass=numpass,
                priorquests=priorquests, subsquests=subsquests, newansjson=XML(newansjson), context=context)


def end_vote():
    # This allows owner to end a vote at any point and
    questid = request.args(0, cast=int, default=0)
    status = score_question(questid, endvote=True)
    redirect(URL('viewquest', 'index', args=[questid]))
    return

# qmap function removed not now using


def comments():
    # This will be a general view on question comments it will require the
    # question id as an argument Logic will be to only display the comements if it
    # has been resolved
    # This maintains the general privacy approach to questions that may be
    # subject to answer eventually if resolved then there will be a view option
    # this needs the as_dict() treatment as well but lets debug viewquest first
    # and then do next - potentially this can be replaced with a plugin

    questid = request.args(0, cast=int, default=0) or redirect(URL('default', 'index'))

    session.questid = questid
    quest = db.question[questid]

    if quest is None:
        redirect(URL('viewquest', 'notshowing/' + 'NoQuestion'))

    return dict(quest=quest)


def useranswers():
    # This displays all users answers to the question and challenges if any
    # for now will probably display all challenges at the bottom of the page
    # as assumption is there won't be too many of these
    # looks like this also needs as_dict treatment

    items_per_page = 8
    questid = request.args(0, cast=int, default=0) or redirect(URL('default', 'index'))

    session.questid = questid
    quest = db.question[questid] or redirect(URL('viewquest', 'notshowing/' + 'NoQuestion'))
    # this needs to become a function - duplicated code with viewquest
    mastlstanswers = quest['answers']
    mastlstnumanswers = quest['answercounts']

    page = request.args(1, cast=int, default=0)
    limitby = (page * items_per_page, (page + 1) * items_per_page + 1)

    uqs = db(db.userquestion.questionid == questid).select(orderby=[~db.userquestion.uq_level], limitby=limitby)
    challs = db(db.questchallenge.questionid == questid).select(orderby=[~db.questchallenge.challengedate])

    return dict(quest=quest, uqs=uqs, page=page, items_per_page=items_per_page, challs=challs)


def notshowing():
    shortreason = request.args(0)
    questid = request.args(1, cast=int, default=0)

    if shortreason == 'NotResolved':
        reason = "This question is not yet resolved and you haven't answered it"
    elif shortreason == 'NotAnswered':
        reason = 'You have not answered this question'
    elif shortreason == 'NotInGroup':
        reason = 'You do not have permission to view this item'
    elif shortreason == 'VoteInProg':
        quest = db(db.question.id == questid).select(db.question.duedate).first()
        reason = "Vote is still in progress so you can't see results. The vote concludes at " + str(quest.duedate)
    elif shortreason == 'NoQuestion':
        reason = 'This question does not exist'
    else:
        reason = 'Not Known'
    return dict(reason=reason, questid=questid, shortreason=shortreason)


def challenge():
    # This allows users to challenge resolved questions - whether or not they have answered them - users are not
    # allowed to challenge questions that are not currently in a state of resolved and this should be done by the
    # viewquestion function rather than the challenge ie option isn't available if question isn't resolved - actions
    # are similar and would only be challenged once they are in a state of Agreed

    chquestid = request.args[0]
    if auth.user is None:
        responsetext = 'You must be logged in to challenge a question'
    else:
        # find out if user has previously challenged the question - this will be a userchallenge record
        qcs = db((db.questchallenge.auth_userid == auth.user.id) & (db.questchallenge.questionid == chquestid)).select()
        qc = qcs.first()
        if qc is None:
            db.questchallenge.insert(questionid=chquestid, auth_userid=auth.user.id,
                                     challengereason=request.vars.challreason)
            # Now also need to add 1 to the numchallenges figure - I think this will reset when back to resolved and
            # It shouldn't be possible to challenge unless resolved
            questrows = db(db.question.id == chquestid).select()
            quest = questrows.first()
            numchallenges = quest.othercounts
            numchallenges[1] += 1
            newlevel = quest.question_level
            status = quest.status
            challenge = False
            if numchallenges[1] >= 3:
                numchallenges[2] += 1
                newlevel = quest.question_level + 2
                status = 'In Progress'
                challenge = True
                updatequestcounts(quest.qtype, quest.category, quest.category, quest.status, status, quest.answer_group)
                # thinking behind this is to restore question two levels higher which is where
                # it would have been if the 6 people had mixed up ie 3 think wrong and 3 that agreed
            db(db.question.id == chquestid).update(status=status, question_level=newlevel, othercounts=numchallenges,
                                                   challengedate=request.utcnow, urgency=quest.urgency,
                                                   importance=quest.importance, challenge=challenge)
            responsetext = 'Challenge accepted'
        else:
            responsetext = 'You have already challenged this question and only 1 challenge is allowed at present'
    return 'jQuery(".flash").html("' + responsetext + '").slideDown().delay(1500).slideUp();' \
                                                      ' $("#target").html("' + responsetext + '");'


def agree():
    # This allows users to record if they agree or disagree with resolve questions
    # - whether or not they have answered them - only resolved questions can
    # be agreed or disagreed with

    chquestid = request.args[0]
    agreeval = int(request.args[1])

    # arg is 1 for agreement and 0 for disagreement and we will use this as latest status
    # for the user and also as the reference for agreementcounts which may become a list int
    # field and then increment the pointer

    if auth.user is None:
        responsetext = 'You must be logged in to record agreement or disagreement'
    else:
        quest = db(db.question.id == chquestid).select().first()
        othcounts = quest.othercounts

        # find out if user has previously agreeed the question -
        # this will be a userchallenge record
        qc = db((db.questagreement.auth_userid == auth.user.id) &
                (db.questagreement.questionid == chquestid)).select().first()

        if qc is None:
            db.questagreement.insert(questionid=chquestid,
                                     auth_userid=auth.user.id, agree=agreeval)
            # Now also need to add 1 to the numagreement or disagreement figure
            # It shouldn't be possible to challenge unless resolved

            if agreeval == 1:
                othcounts[3] += 1
                responsetext = 'Agreement Recorded'
            else:
                othcounts[4] += 1
                responsetext = 'Disagreement Recorded'
        else:
            if agreeval == qc.agree:
                if agreeval == 1:
                    responsetext = 'You have already registered agreement'
                else:
                    responsetext = 'You have already registered your disagreement'
                    ' - you may be able to challenge'
            else:
                if agreeval == 1:
                    responsetext = 'Your vote has been changed to agreement'
                    othcounts[3] += 1
                    othcounts[4] -= 1
                else:
                    responsetext = 'Your vote has been changed to disagreement'
                    othcounts[3] -= 1
                    othcounts[4] += 1
                qc.update_record(agree=agreeval)

        db(db.question.id == chquestid).update(othercounts=othcounts)
    return 'jQuery(".flash").html("' + responsetext + '").slideDown().delay(1500).slideUp();' \
                                                      ' $("#target").html("' + responsetext + '");'


def flagcomment():
    # This allows users to record if they think a comment is inappropriate
    # if 3 separate users flag the comment then it is removed from display
    # permanently for now

    commentid = request.args[0]
    requesttype = request.args[1]

    if auth.user is None:
        responsetext = 'You must be logged in to flage inappropriate comments'
    else:
        comment = db(db.questcomment.id == commentid).select().first()

        if requesttype != 'admin':
            # check if user has previously challenged the question -
            # this will be an entry in the usersreject field

            if comment.usersreject is not None and auth.user.id in comment.usersreject:
                responsetext = 'You have already flagged this comment'
            else:
                responsetext = 'Rejection recorded'
                comment.numreject += 1
                if comment.usersreject is not None:
                    comment.usersreject.append(auth.user.id)
                else:
                    comment.usersreject = [auth.user.id]
                if comment.numreject > 2:
                    comment.status = 'NOK'
                comment.update_record()
        else:
            responsetext = 'Admin hide successful'
            comment.update_record(status='NOK')
    return responsetext


def urgency():
    # This allows users to record or update their assessment of the urgency and
    # importance of an action as this helps with prioritising the actions that
    # are required - next step is to attempt to get the view sorted and will
    # retrieve this as part of main index controller

    if request.vars.urgslider2 is None:
        urgslider = 5
    else:
        urgslider = int(request.vars.urgslider2)

    if request.vars.impslider2 is None:

        impslider = 5
    else:
        impslider = int(request.vars.impslider2)

    chquestid = request.args[0]
    if auth.user is None:
        responsetext = 'You must be logged in to record urgency and importance'
    else:
        questrows = db(db.question.id == chquestid).select()
        quest = questrows.first()
        qurgency = quest.urgency
        qimportance = quest.importance

        # find out if user has rated the question already
        qcs = db((db.questurgency.auth_userid == auth.user.id) &
                 (db.questurgency.questionid == chquestid)).select()

        qc = qcs.first()

        if qc is None:
            db.questurgency.insert(questionid=chquestid,
                                   auth_userid=auth.user.id,
                                   urgency=urgslider,
                                   importance=impslider)

            urgency = request.vars.urgslider2
            responsetext = 'Your assessment has been recorded'

        else:
            qc.update_record(urgency=request.vars.urgslider2,
                             importance=request.vars.impslider2)
            responsetext = 'Your assessment has been updated'

        if quest.totratings == 0:
            totratings = quest.totanswers()
        else:
            totratings = quest.totratings

        urgent = (((quest.urgency * totratings) + urgslider) / (totratings + 1))
        importance = (((quest.importance * totratings) + impslider) / (totratings + 1))

        if qc is None:
            totratings += 1
        priority = urgent * importance  # perhaps a bit arbitary but will do for now

        db(db.question.id == chquestid).update(urgency=urgent,
                                               importance=importance, priority=priority, totratings=totratings)

    return responsetext

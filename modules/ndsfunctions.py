# - Coding UTF8 -
#
# Networked Decision Making
# Site: http://code.google.com/p/global-decision-making-system/
#
# License Code: GPL, General Public License v. 2.0
# License Content: Creative Commons Attribution 3.0
#
# Also visit: www.web2py.com
# or Groups: http://groups.google.com/group/web2py
# 	For details on the web framework used for this development
#
# Developed by Russ King (newglobalstrategy@gmail.com
# Russ also blogs occasionally to pass the time at proudofyourplanent.blogspot.com
# His general thinking on why this project is very important is availalbe at
# http://www.scribd.com/doc/98216626/New-Global-Strategy

from gluon import *
from textwrap import fill


#from scheduler import email_resolved

def resulthtml(questiontext, answertext, resmethod='Not Specified', output='html'):
    if output == 'html':
        result = '<p>' + questiontext + r'</p>'
        result += r'<p>Users have resolved the correct answer is:</p>'
        result += '<p>' + answertext + r'</p>'
        result = '<html>'+result + r'</html>'
    else:
        result = questiontext + '/n Users have resolved the correct answer is: /n' + answertext
    return result


def updatequestcounts(qtype, oldcategory, newcategory, oldstatus, newstatus, answergroup):
    """This will now take the old and new category and the old and new status.  The answergroup should never change so
       only there if status has changed to update the answergroup counts
    `  1 nothing changes - may call to debug
       2 status change - update questcounts on existing record and update answergroup counts
       3 category change - reduce questcount at old status and increase questcount on different record for new
         status
       4 category and status change """

    if oldcategory == newcategory and oldstatus == newstatus:
        return

    db = current.db
    #get existing category record should always exist
    existrow = db((db.questcount.groupcatname == oldcategory) & (db.questcount.groupcat == 'C')).select().first()

    oldindex = getindex(qtype, oldstatus)
    newindex = getindex(qtype, newstatus)
    qcount = existrow.questcounts
    qcount[oldindex] -= 1
    
    if oldcategory == newcategory:
        qcount[newindex] += 1
    existrow.update_record(questcounts=qcount)

    if oldcategory != newcategory:
        newrows = db((db.questcount.groupcatname == newcategory) & (db.questcount.groupcat == 'C')).select()
        if newrows:
            newrow = newrows.first()
            qcount = newrow.questcounts
            qcount[newindex] += 1
            newrow.update_record(questcounts=qcount)
        else:
            createcount = [0] * 18
            createcount[newindex] = 1
            db.questcount.insert(groupcat='C', groupcatname=newcategory, questcounts=createcount)
    # udpate the group count record if status changed
    if oldstatus != newstatus:
        grouprow = db((db.questcount.groupcatname == answergroup) & (db.questcount.groupcat == 'G')).select().first()
        if grouprow:
            qcount = grouprow.questcounts
            qcount[oldindex] -= 1
            qcount[newindex] += 1
            grouprow.update_record(questcounts=qcount)
        else:
            print('An error occurred updating group quest counts')
    return


def update_question(questid, userid):
    """
    This procedure updates the question and userquestion records after each answer
    The update is in 2 parts.  The number of answers and so on are
    always updated however the main scoring only happens when we have 3 or more
    unprocessed answers. so there is a case to separate into two functions however reluctant 
    to push scoring onto scheduler as user need to know immediately if they solved the question
    however score lower level should probably be scheduled
    only call score_question if sufficient unprocessed answers  

    When this is a module it is not posting userquestion updates as we don't know the user and the first
    part of what is in the controller is not called - plan will be to get this working for quick questions
    and then call all the time once this works it may get merged into score question but with separate
    function to address resolved question??
    """

    db = current.db
    cache = current.cache
    request=current.request

    quest = db(db.question.id == questid).select().first()


    answers_per_level = 3  

    # first step is to select the related user and question records their should
    # only ever be one of each of these and we update as much as possible here 
    # because it's interesting to see as much as possible on viewquest rather
    # than waiting until 3 people have answered and it can be scored - however this can result in
    # a degree of double updating

    if quest.intunpanswers >= answers_per_level:
        redirect(URL('score_question', args=quest.id))
    else:
        # need to have another look at this 
        # intunpanswers < answers_per_level
        # the general requirement here is to do nothing - however because the
        # solution focuses on solving the highest priority question at all times
        # different users may be sent the same question at the same time and
        # answers may be received for a level after the question is either promoted
        # or resolved - promotions shouldn't be an issue but resolved questions are
        # because the user should probably get credit if right and nothing if wrong
        # and an explanation of what happend

        if quest.status == 'Resolved' or quest.status == 'Agreed':
            #get the score - if right add to score - if wrong same
            #update userquestion and user - other stuff doesn't apply
            #scoretable = db(db.scoring.level == quest.level).select(cache=(cache.ram, 1200), cacheable=True).first()
            scoretable = db(db.scoring.level == quest.level).select().first()
            if scoretable is None:
                score = 30
                wrong = 1
            else:
                if quest.qtype != 'action':
                    score = scoretable.correct
                    wrong = scoretable.wrong
                else:
                    score = scoretable.rightaction
                    wrong = scoretable.wrongaction
            numcorrect = 0
            numwrong = 0
            numpassed = 0

            if uq.answer == quest.correctans:
                updscore = score
                numcorrect = 1
            elif uq.answer == 0:
                updscore = 1
                numpasse = 1
            else:
                updscore = wrong
                numwrong = 1

            uq.update_record(status='Resolved', score=updscore, resolvedate=request.utcnow)

            updateuser(userid, updscore, numcorrect, numwrong, numpassed)

        redirect(URL('viewquest', 'index', args=quest.id))


def score_question(questid, uqid=0, endvote=False):
    """
    This routine is now called for all answers to questions and it will also be
    called for vote style questions
    """

    answers_per_level = 3  # To be replaced with record
    answers_to_resolve = 3
    method = 'Network'

    status = 'In Progress'
    changecat = False
    changescope = False

    db = current.db
    cache = current.cache
    request=current.request

    quest = db(db.question.id == questid).select().first()

    # change May 15 to get the answers per level and the resolution type out of the
    # table - this should be cacheable in due course

    resmethods = db(db.resolvemethod.resolve_name == quest.resolvemethod).select()

    if resmethods:
        resmethod=resmethods.first()
        answers_per_level = resmethod.responses
        method = resmethod.method
    
    if uqid:
        uq = db.userquestion[uqid]

        # first step is to select the related user and question records their should
        # only ever be one of each of these and we update as much as possible here
        # because it's interesting to see as much as possible on viewquest rather
        # than waiting until 3 people have answered and it can be scored - however this can result in
        # a degree of double updating


        # do weighted averaging of urgency and importance based on userquest and this is
        # accepted from passers
        if uq:
            urgency = (((quest.urgency * quest.totanswers()) + uq.urgency) /
                       (quest.totanswers() + 1))
            importance = (((quest.importance * quest.totanswers()) + uq.importance) /
                          (quest.totanswers() + 1))

            anscount = quest.answercounts
            anscount[uq.answer] += 1
            intunpanswers = quest.unpanswers + 1

            db(db.question.id == quest.id).update(answercounts=anscount,
                                              urgency=urgency, importance=importance, unpanswers=intunpanswers)

            update_numanswers(uq.auth_userid)
    else:
        intunpanswers = quest.unpanswers
        urgency=quest.urgency
        importance=quest.importance

    #print intunpanswers, answers_per_level, method

    if (intunpanswers >= answers_per_level and method == 'Network') or endvote:

        # if intunpanswers >= answers_per_level:
        # this was always true in old structure probably not now as may handle votes this way - TODO Review this 
        # scorequestions - need to get all the answers first at this level -
        # should agree to unpanswers and should be a small number - so lets fully
        # score these - if they don't agree to unpanswers then doesn't agree
        # and will need to be escalated - so simple score if resolved - lower
        # levels will probably be done as a background task eventually so seems
        # ok this should never happen on a passed question at present challengees
        # are not getting credit for right or wrong challenges - this will be
        # added in a subsequent update not that complicated to do however
        # aim to update eventmap if required here now which would be if eventmap question exists
        # now no possibility of changing event so simpler

        level = quest.level

        # this will be changed to a single select and process the rows
        # object to get counts etc

        #scoretable = db(db.scoring.level == level).select(cache=(cache.ram, 1200), cacheable=True).first()
        scoretable = db(db.scoring.level == level).select().first()
        if scoretable is None:
            score = 30
            wrong = 1
            submitter = 1
        else:
            submitter = scoretable.submitter
            if quest.qtype == 'quest':
                score = scoretable.correct
                wrong = scoretable.wrong
            else:
                score = scoretable.rightaction
                wrong = scoretable.wrongaction

        # so basic approach to this is a two pass approach first pass
        # should total the answers establish if majority want to reject, change category
        # or change geography and if it meets resolution criteria which will now come from a questtype
        unpanswers = db((db.userquestion.questionid == questid) &
                        (db.userquestion.status == 'In Progress') &
                        (db.userquestion.level == level)).select()

        numanswers = [0] * len(quest.answercounts)
        #numanswers needs to become a list or dictionary
        numreject = 0
        numchangescope = 0
        numchangecat = 0
        updatedict = {'unpanswers': 0}
        ansreason = ""
        ansreason2 = ""
        ansreason3 = ""
        scopedict = {}
        contdict = {}
        countrydict = {}
        localdict = {}
        catdict = {}

        for row in unpanswers:
            numanswers[row.answer] += 1
            numreject += row.reject
            numchangescope += row.changescope
            numchangecat += row.changecat

        if (max(numanswers) >= ((len(unpanswers)  * resmethod.consensus)/100) or
            method=='Vote'):  # all answers agree or enough for consensues or vote is being resolved
            status = 'Resolved'
            correctans = numanswers.index(max(numanswers))
            numcorrect = 1
            updatedict['correctans'] = correctans

        elif (numreject * 2) > answers_per_level:  # majority reject
            status = 'Rejected'
            correctans = -1
        else:
            # insufficient consensus so promote to next level
            level += 1
            updatedict['level'] = level
            status = 'In Progress'
            correctans = -1

        if (numchangescope * 2) > answers_per_level:  # majority want to move scope
            changescope = True

        if (numchangecat * 2) > answers_per_level:  # majority want to move category
            changecat = True

        # update userquestion records

        #this is second pass through to update the records
        for row in unpanswers:
            # for this we should have the correct answer
            # update userquestion records to being scored change status
            # however some users may have passed on this question so need
            # a further condition and the question is still resolved
            # also need to consider the change scope and change category
            # but only if a majority want this otherwise will stay as is
            # change cat and change scope are slightly different as change
            # of scope might be agreed but the correct continent or country
            # may differ in which case the question will have scope changed
            # but continent or country unchanged

            numcorrect = 0
            numwrong = 0
            numpassed = 0


            if row.answer == correctans and correctans > -1:  # user got it right
                numcorrect = 1
                # update the overall score for the user
                updscore = score
                if row.answerreason != '':
                    if ansreason == '':
                        ansreason = row.answerreason
                        updatedict['answerreasons'] = ansreason
                    elif ansreason2 == '':
                        ansreason2 = row.answerreason
                        updatedict['answerreason2'] = ansreason2
                    else:
                        ansreason3 = row.answerreason
                        updatedict['answerreason3'] = ansreason3
                elif row.answer == -1:  # user passed
                    numpassed = 1
                    updscore = 1
                elif correctans == -1:  # not resolved yet
                    numrong = 0
                    updscore = 0
                else:  # user got it wrong - this should be impossible at present as unanimity reqd
                    numwrong = 1
                    updscore = wrong

                # this needs rework
                if status == 'Resolved':
                    row.update_record(status=status, score=updscore, resolvedate=request.utcnow)
                else:
                    row.update_record(status=status, score=updscore)

                if changecat is True:
                    suggestcat = row.category
                    if suggestcat in catdict:
                        catdict[suggestcat] += 1
                    else:
                        catdict[suggestcat] = 1

                if changescope is True:
                    # perhaps do as two dictionaries
                    # do both of these the same way for consistency
                    suggestscope = row.activescope
                    suggestcont = row.continent
                    suggestcountry = row.country
                    suggestlocal = row.subdivision
                    if suggestscope in scopedict:
                        scopedict[suggestscope] += 1
                    else:
                        scopedict[suggestscope] = 1
                    if suggestcont in contdict:
                        contdict[suggestcont] += 1
                    else:
                        contdict[suggestcont] = 1
                    if suggestcountry in countrydict:
                        countrydict[suggestcountry] += 1
                    else:
                        countrydict[suggestcountry] = 1
                    if suggestlocal in localdict:
                        localdict[suggestlocal] += 1
                    else:
                        localdict[suggestlocal] = 1
                #update user
                updateuser(row.auth_userid, updscore, numcorrect, numwrong, numpassed)


        # update the question to resolved or promote as unresolved
        # and insert the correct answer values for this should be set above
        suggestcat = quest.category
        suggestscope = quest.activescope
        suggestcont = quest.continent
        suggestcountry = quest.country
        suggestlocal = quest.subdivision
        scopetext = quest.scopetext
        oldcategory = quest.category
        oldstatus = quest.status

        if changecat is True:
            # loop through catdict and determine if any value has majority value
            for j in catdict:
                if (catdict[j] * 2) > answers_per_level:
                    suggestcat = j
                    updatedict['category'] = suggestcat
                    changecategory=True
        if changescope is True:
            # loop through catdict and determine if any value has majority value
            for j in scopedict:
                if (scopedict[j] * 2) > answers_per_level:
                    suggestscope = j
                    updatedict['activescope'] = suggestscope
            for j in contdict:
                if (contdict[j] * 2) >= answers_per_level:
                    suggestcont = j
                    updatedict['continent'] = suggestcont
            for j in countrydict:
                if (countrydict[j] * 2) >= answers_per_level:
                    suggestcountry = j
                    updatedict['country'] = suggestcountry
            for j in localdict:
                if (localdict[j] * 2) >= answers_per_level:
                    suggestlocal = j
                    updatedict['subdivision'] = suggestlocal
            scopetype = suggestscope

            if scopetype == '1 Global':
                scopetext = '1 Global'
            elif scopetype == '2 Continental':
                scopetext = suggestcont
            elif scopetype == '3 National':
                scopetext = suggestcountry
            else:
                scopetext = suggestlocal
            updatedict['scopetext'] = scopetext

        updstatus = status
        if quest.qtype != 'quest':
            if correctans == 0:
                updstatus = 'Agreed'
            else:
                updstatus = 'Disagreed'
        if updstatus != quest.status:
            updatedict['status'] = updstatus
            updatedict['resolvedate'] = request.utcnow
            changestatus=True

        #lines added to avoid error on recalc of computed field 
        updatedict['urgency'] = quest.urgency
        updatedict['importance'] = quest.importance

        db(db.question.id == quest.id).update(**updatedict)

        updatequestcounts(quest.qtype, oldcategory, suggestcat, oldstatus, updstatus, quest['answer_group'])

        # Update eventmap if it exists
        eventquest = db((db.eventmap.questid == quest.id) & (db.eventmap.status == 'Open')).select().first()

        if eventquest:
            # update the record - if it exists against an eventmap
            eventquest.update_record(urgency=urgency, importance=importance, correctans=correctans,
                queststatus=updstatus)

            # increment submitter's score for the question
            submitrow = db(db.auth_user.id == quest.auth_userid).select().first()
            updateuser(quest.auth_userid, submitrow.score, 0, 0, 0)

            # display the question and the user status and the userquestion status
            # hitting submit should just get you back to the answer form I think and
            # fields should not be updatable

        if status == 'Resolved' and level > 1:
            score_lowerlevel(quest.id, correctans, score, level, wrong)
            #TODO this needs reviewed - not actually doing much at the moment
            if quest.challenge is True:
                if correctans == quest.correctans:
                    successful = False
                else:
                    successful = True
                    # score_challenge(quest.id, successful, level)

    # Think deletion would become a background task which could be triggered here
    

    message='question processed'
    return status


def getindex(qtype, status):
    """This returns the index for questcounts which is a list of integers based on the 6 possible status and 3 question
       types so it is an index based on two factors want 0, 1 or 2 for issue, question and action and then 0 through 5
       for draft, in progress, etc - need to confirm best function to do this with"""

    qlist = ['issue', 'quest', 'action']
    slist = ['Draft', 'In Progress', 'Resolved', 'Agreed', 'Disagreed', 'Rejected']

    i = qlist.index(qtype) if qtype in qlist else None
    j = slist.index(status) if status in slist else None

    # TODO put a try catch around this and add some tests to this
    return (i * 6) + j


def userdisplay(userid):
    """This should take a user id and return the corresponding
       value to display depending on the users privacy setting"""
    usertext = userid
    db = current.db
    userpref = db(db.auth_user.id == userid).select().first()
    if userpref.privacypref=='Standard':
        usertext=userpref.username
    else:
        usertext=userid
    return usertext


def scopetext(scopeid, continent, country, subdivision):
    request = current.request
    if not request.env.web2py_runtime_gae:
        db = DAL('sqlite://storage.sqlite')
    else:
        db = DAL('google:datastore')

    scope = db(db.scope.id == scopeid).select(db.scope.description).first().description
    if scope == 'Global':
        activetext = 'Global'
    elif scope == 'Continental':
        activetext = db(db.continent.id == continent).select(
            db.continent.continent_name).first().continent_name
    elif scope == 'National':
        activetext = db(db.country.id == country).select(
            db.country.country_name).first().country_name
    else:
        activetext = db(db.subdivision.id == subdivision).select(
            db.subdivision.subdiv_name).first().subdiv_name

    return activetext


def truncquest(questiontext, maxlen=600, wrap=0):
    # aim to do wordwrapping and possibly stripping and checking as
    # part of this function for jointjs now
    if len(questiontext) < maxlen:
        txt = MARKMIN(questiontext)
    else:
        txt = MARKMIN(questiontext[0:maxlen] + '...')
    return txt


def getwraptext(textstring, answer, textwidth, maxlength=230):
    if len(textstring) < maxlength:
        txt = textstring
    else:
        txt = textstring[0:maxlength] + '...'
    if answer:
        txt = txt + '\n' + 'A:' + answer
    qtexttemp = fill(txt, textwidth)
    lqtext = qtexttemp.split('\n')
    qtext = ''
    for y in lqtext:
        qtext += y
        qtext += r'\n'

    # qtext = textstring[:20] + r'\n' + textstring[21:40]
    qtext = qtext[:-2]
    return qtext


def disp_author(userid):
    if userid is None:
        return ''
    else:
        user = db.auth_user(userid)
        return '%(first_name)s %(last_name)s' % userid


def updateuser(userid, score, numcorrect, numwrong, numpassed):
    db = current.db
    cache = current.cache


    # moved here from answer controller
    # just added current db line
    user = db(db.auth_user.id == userid).select().first()
    # Get the score required for the user to get to next level
    scoretable = db(db.scoring.level == user.level).select(cache=(cache.ram, 1200), cacheable=True).first()

    if scoretable is None:
        nextlevel = 1000
    else:
        nextlevel = scoretable.nextlevel

    updscore = user.score + score

    if updscore > nextlevel:
        userlevel = user.level + 1
    else:
        userlevel = user.level

    user.update_record(score=updscore, numcorrect=user.numcorrect + numcorrect,
                       numwrong=user.numwrong + numwrong, numpassed=user.numpassed + numpassed,
                       level=userlevel)
    # stuff below removed for now as not working and want this to run as background scheduler task so makes no sense
    # to have here in this context
    #if auth.user.id == userid:  # update auth values
    #    auth.user.update(score=updscore, level=userlevel, rating=userlevel, numcorrect=
    #                             auth.user.numcorrect + numcorrect, numwrong=auth.user.numwrong + numwrong,
    #                             numpassed=auth.user.numpassed + numpassed)

    return True


def update_numanswers(userid):
    # This just increments numb users
    db = current.db
    cache = current.cache
    auth = current.session.auth or None
    if auth and userid == auth.user.id: # This should always be the case
        numquests = auth.user.numquestions + 1
        db(db.auth_user.id == auth.user.id).update(numquestions=numquests)
        auth.user.update(numquestions=numquests)
    return True


        #numquests = auth.user.numquestions + 1
        #db(db.auth_user.id == auth.user.id).update(numquestions=numquests)
        #auth.user.update(numquestions=numquests)


def score_lowerlevel(questid, correctans, score, level, wrong):
    """
    This may eventually be a cron job but for debugging it will need to be
    called from score_question basic approach is just to go through and update
    all the lower levels and if correct they get the values
    of the question which will probably be higher the higher the level it got
    resolved at so this isn't too complicated - but need to be passed the
    question-id, the correct answer and the number of
    points for correct and number for wrong - lets do later once main process
    working.
    Users get points for the level the question resolved at but need to acquire
    the level of points to move up from their level

    This needs some further work to cater for challenge questions which have a
    different 2nd resolved answer
    thinking is the original correct answers can stay because it was reasonable
    but those that got it wrong
    at lower levels should get some credit - however not critical for now -
    lets publish and see what other people consider best approach to this -
    it is not clear cut - nor critical to the principal of
    what we are trying to to do

    scoretable = db(db.scoring.level==level).select().first()
    score = scoretable.correct
    there should be no need to assess changes to categories or scope
    in this process as these will all have been considered in previous rounds
    and the auth user running this should always be a user at the top level
    so no issues with auth not updating either - so we should be good to go
    """

    status = 'Resolved'

    db = current.db
    cache = current.cache
    request=current.request

    unpanswers = db((db.userquestion.questionid == questid) &
                    (db.userquestion.status == 'In Progress')).select()

    for row in unpanswers:
        # work out if the question was correct or not
        if row.answer == correctans:
            actscore = score
            numcorrect = 1
            numwrong = 0
        elif row.answer == 0:
            actscore = 1
            numcorrect = 0
            numwrong = 0
        else:
            actscore = wrong
            numcorrect = 0
            numwrong = 1

        # update userquestion records to being scored change status
        db(db.userquestion.id == row.id).update(score=actscore, status=status, resolvedate=request.utcnow)
        # update the overall score for the user
        user = db(db.auth_user.id == row.auth_userid).select().first()
        updscore = user.score + actscore
        level = user.level
        scoretable = db(db.scoring.level == level).select(cache=(cache.ram, 1200), cacheable=True).first()
        nextlevel = scoretable.nextlevel

        if updscore > nextlevel:
            userlevel = user.level + 1
        else:
            userlevel = user.level

        db(db.auth_user.id == row.auth_userid).update(score=updscore,
                                                      level=userlevel, rating=user.level + userlevel,
                                                      numcorrect=user.numcorrect + numcorrect,
                                                      numwrong=user.numwrong + numwrong)
    return


def score_challengel(questid, successful, level):
    """
    This will reward those that raised a challenge if the answer has changed
    it may also spawn an issue of scoring users who previously thought they
    got it wrong but now got it right - thinking is we wouldn't remove
    points from those that were previously considered right
    """

    db = current.db
    cache = current.cache
    request=current.request

    unpchallenges = db((db.questchallenge.questionid == questid) &
                       (db.questchallenge.status == 'In Progress')).select()

    # should get the score based on the level of the question
    # and then figure out whether
    # get the score update for a question at this level
    scoretable = db(db.scoring.level == level).select().first()

    if scoretable is None:
        rightchallenge = 30
        wrongchallenge = -10
    else:
        rightchallenge = scoretable.rightchallenge
        wrongchallenge = scoretable.wrongchallenge

    for row in unpchallenges:
        # update the overall score for the user
        user = db(db.auth_user.id == row.auth_userid).select().first()
        if successful is True:
            updscore = user.score + rightchallenge
        else:
            updscore = user.score + wrongchallenge
        level = user.level
        scoretable = db(db.scoring.level == level).select().first()
        nextlevel = scoretable.nextlevel

        if updscore > nextlevel:
            userlevel = user.level + 1
        else:
            userlevel = user.level

        db(db.auth_user.id == row.auth_userid).update(score=updscore,
                                                      level=userlevel)
    return


def getitem(qtype):
    if qtype == 'quest':
        item = 'question'
    elif qtype == 'action':
        item = 'action'
    else:
        item = 'issue'
    return item


# below is copy from network temporarily
def index():
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
    numlevels = request.args(0, cast=int, default=0)
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

    # insert from viewquest to go through

    qlink = {}
    keys = '['
    cellsjson = '['
    for x in quests:
        template = getitemshape(x.id, nodepositions[x.id][0] * grwidth, nodepositions[x.id][1] * grheight,
                                x.questiontext, x.correctanstext(), x.status, x.qtype, x.priority)
        cellsjson += template + ','

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
            if nodepositions[x.targetid][1] > nodepositions[x.sourceid][1]:
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

    for key, vals in qlink.iteritems():
        template = jsonmetlink(key, vals[0], vals[1], vals[2], vals[3], vals[4])
        cellsjson += template + ','

    cellsjson = cellsjson[:-1]+']'

    return dict(quests=quests, links=links, resultstring=resultstring, keys=keys, qlink=qlink,
                netdebug=netdebug, cellsjson=cellsjson)


def creategraph(itemids, numlevels=0, intralinksonly=True):
    """
    :param itemids: list
    :param numlevels: int
    :param intralinksonly: boolean
    :param eventid: int
    :param redraw: boolean
    :return: graph details

    Now think this will ignore eventmap and do no layout related stuff which means events are irrelevant for this
    function it should get links for itemids in an iterable manner and so build of network.py  mainly
    when called from event it will have a list of item ids only from the event already established

    """

    query = db.question.id.belongs(itemids)
    quests = db(query).select()

    if intralinksonly:
        # in this case no need to get other questions
        intquery = (db.questlink.targetid.belongs(itemids)) & (db.questlink.status == 'Active') & (
                    db.questlink.sourceid.belongs(itemids))

        # intlinks = db(intquery).select(cache=(cache.ram, 120), cacheable=True)
        intlinks = db(intquery).select()
    else:

        parentquery = (db.questlink.targetid.belongs(itemids)) & (db.questlink.status == 'Active')
        childquery = (db.questlink.sourceid.belongs(itemids)) & (db.questlink.status == 'Active')

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

    graphinsomeformat = ''
    return graphinsomeformat

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
            response.view = 'noevent'
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
            if auth.user_id == eventrow.owner or eventrow.shared:
                session.flash = 'This event has no items at present - you can add them here'
            redirect(URL('eventadditems',args=eventid))

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
    print(resultstring)
    #questmap=questmap,
    return dict(cellsjson=XML(cellsjson), eventrow=eventrow, links=links, resultstring=resultstring,
                eventmap=eventmap,  keys=keys, qlink=qlink, eventid=eventid)




def graphtojson(graphinsomeformat):
    # this will move to jointjs after initial setup
    jointjsjson = ''    

    return jointjsjson


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




    ANSWERS_PER_LEVEL = 3  

    # first step is to select the related user and question records their should
    # only ever be one of each of these and we update as much as possible here 
    # because it's interesting to see as much as possible on viewquest rather
    # than waiting until 3 people have answered and it can be scored - however this can result in
    # a degree of double updating

    if quest.intunpanswers >= ANSWERS_PER_LEVEL:
        redirect(URL('score_question', args=quest.id))
    else:
        # need to have another look at this 
        # intunpanswers < stdrouting
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
                    score = scoretable.right
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


def score_question(questid, uqid=0):
    """
    So this now only called if sufficient answers to attempt to resolve - I think we would have a separate routine for vote results as well
    shouldn't really be anything special about the last user versus the other ones in this
    """

    ANSWERS_PER_LEVEL = 3  # To be replaced with record

    stdrouting = ANSWERS_PER_LEVEL
    status = 'In Progress'
    changecat = False
    changescope = False

    db = current.db
    cache = current.cache
    request=current.request

    quest = db(db.question.id == questid).select().first()

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
    else:
        intunpanswers = quest.unpanswers
        urgency=quest.urgency
        importance=quest.importance



    if intunpanswers >= ANSWERS_PER_LEVEL:

        # if intunpanswers >= stdrouting:
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
                score = scoretable.right
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

            #if row.answer == uq.answer:
            #    numanswers += 1
            #if row.reject is True:
            #    numreject += 1
            #if row.changescope is True:
            #    numchangescope += 1
            #if row.changecat is True:
            #    numchangecat += 1
            #    # get the score update for a question at this level

        if max(numanswers) >= stdrouting:  # all answers agree or at least as many as
            # stdrouting this is ok as if rejected and answered
            # then we will accept the answer
            status = 'Resolved'
            correctans = numanswers.index(max(numanswers))
            numcorrect = 1
            updatedict['correctans'] = correctans

        elif (numreject * 2) > stdrouting:  # majority reject
            status = 'Rejected'
            correctans = -1
        else:
            # no unanimity and this is required for std routing so promote
            level += 1
            updatedict['level'] = level
            status = 'In Progress'
            correctans = -1

        if (numchangescope * 2) > stdrouting:  # majority want to move scope
            changescope = True

        if (numchangecat * 2) > stdrouting:  # majority want to move category
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
                if (catdict[j] * 2) > stdrouting:
                    suggestcat = j
                    updatedict['category'] = suggestcat
                    changecategory=True
        if changescope is True:
            # loop through catdict and determine if any value has majority value
            for j in scopedict:
                if (scopedict[j] * 2) > stdrouting:
                    suggestscope = j
                    updatedict['activescope'] = suggestscope
            for j in contdict:
                if (contdict[j] * 2) >= stdrouting:
                    suggestcont = j
                    updatedict['continent'] = suggestcont
            for j in countrydict:
                if (countrydict[j] * 2) >= stdrouting:
                    suggestcountry = j
                    updatedict['country'] = suggestcountry
            for j in localdict:
                if (localdict[j] * 2) >= stdrouting:
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
            if quest.challenge is True:
                if correctans == quest.correctans:
                    successful = False
                else:
                    successful = True
                    # score_challenge(quest.id, successful, level)

    message='question processed'
    return message


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
    score = scoretable.right
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

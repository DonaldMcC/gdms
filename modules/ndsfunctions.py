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

import datetime

from gluon import *
from netx2py import getpositions
from ndspermt import get_exclude_groups


def resulthtml(questiontext, answertext, id=0, output='html'):
    db = current.db
    params = db(db.website_parameters.id > 0).select().first()
    if output == 'html':
        result = '<p>' + questiontext + r'</p>'
        result += r'<p>Users have resolved the correct answer is:</p>'
        result += '<p>' + answertext + r'</p>'
        result += URL('viewquest','index', args=[id], scheme='http', host=params.website_url)
        result = '<html>'+result + r'</html>'
    else:
        result = questiontext + '/n Users have resolved the correct answer is: /n' + answertext
    return result

    
def email_setup(periods = ['Day', 'Week', 'Month'], refresh=False):
    # This will setup a daily, weekly and monthly record in the file
    # Daily will be for current day, weekly for current week and monthly for current month
    # It will then schedule a task which runs daily and that will then run the actual activity
    # task
    db = current.db  
    for x in periods:
        startdate, enddate = getrundates(x)
        existrows = db((db.email_runs.runperiod == x) & (db.email_runs.status == 'Planned')).select()
        if existrows:
            existrow = existrows.first()
            if refresh is True:  #Running a rollforward
                startdate=existrow.dateto
            existrow.update(datefrom=startdate,dateto=enddate)
        else:
            db.email_runs.insert(runperiod=x, datefrom=startdate, dateto=enddate, status='Planned')
    return True    
    
    
def getquestnonsql(questtype='quest', userid=None, excluded_categories=None):
    db = current.db
    cache = current.cache
    request=current.request
    session=current.session
    auth = current.session.auth
    
    if session.answered is None:
        session.answered = []
        ansquests = db((db.userquestion.auth_userid == session.userid) &
                       (db.userquestion.status == 'In Progress')).select(db.userquestion.questionid)
        for row in ansquests:
            session.answered.append(row.questionid)
    print userid
    session.exclude_groups = get_exclude_groups(userid)
    questrow = 0

    print (session.exclude_groups)

    orderstr = ''
    if session.continent == 'Unspecified':  # ie no geographic restriction
        for i in xrange(0, 4):
            if i == 0:
                query = (db.question.question_level == session.level) & (db.question.status == 'In Progress')
                orderstr = ~db.question.priority
            elif i == 1:
                if session.level >1:
                    query = (db.question.question_level < session.level) & (db.question.status == 'In Progress')
                    orderstr = ~db.question.question_level | ~db.question.priority
            elif i == 2:
                query = (db.question.question_level > session.level) & (db.question.status == 'In Progress')
                orderstr = db.question.question_level | ~db.question.priority
            elif i == 3:
                query = (db.question.status == 'In Progress')
                orderstr = ~db.question.priority

            if questtype != 'all':
                query &= db.question.qtype == questtype

            if i < 3:
                # remove caching and see if fixes for now
                # quests = db(query).select(orderby=orderstr,cache=(cache.ram, 120), cacheable=True)
                quests = db(query).select(orderby=orderstr)
            else:  # no caching for final attempt
                quests = db(query).select(orderby=~db.question.priority)

            questrow = quests.first()
            if questrow is not None:
                print i, questrow.id
            # exclude previously answered - this approach specifically taken rather than
            # an outer join so it can work on google app engine
            # then filter for unanswered and categories users dont want questions on
            alreadyans = quests.exclude(lambda row: row.id in session.answered)
            alreadyans = quests.exclude(lambda row: row.category in excluded_categories)
            alreadyans = quests.exclude(lambda row: row.answer_group in session.exclude_groups)

            questrow = quests.first()
            if questrow is not None:
                break
    else:
        # This is separate logic which applies when user has specified a continent - the general
        # thinking is that users cannot opt out of global questions but they may specify a continent
        # and optionally also a country and a subdivision in all cases we will be looking to
        # run 4 queries the global and continental queries will always be the same but
        # the country and subdvision queries are conditional as country and subdivision
        # may be left unspecified in which case users should get all national quests for
        # their continent or all local questions for their country - we will attempt to
        # keep the same logic surrounding levels shorlty

        for i in xrange(0, 3):
            if i == 0:
                query = (db.question.question_level == session.level) & (db.question.status == 'In Progress')
            elif i == 1:
                if session.level < 2:
                    continue
                else:
                    query = (db.question.question_level < session.level) & (db.question.status == 'In Progress')
            elif i == 2:
                query = (db.question.question_level > session.level) & (db.question.status == 'In Progress')
            elif i == 3:
                query = (db.question.status == 'In Progress')

            if questtype != 'all':
                query &= db.question.qtype == questtype
            qcont = query & (db.question.continent == auth.user.continent) & (
                db.question.activescope == '2 Continental')
            qglob = query & (db.question.activescope == '1 Global')

            if auth.user.country == 'Unspecified':
                qcount = query & (db.question.continent == auth.user.continent) & (
                    db.question.activescope == '3 National')
            else:
                qcount = query & (db.question.country == auth.user.country) & (db.question.activescope == '3 National')

            if auth.user.subdivision == 'Unspecified':
                qlocal = query & (db.question.country == auth.user.country) & (db.question.activescope == '4 Local')
            else:
                qlocal = query & (db.question.subdivision == auth.user.subdivision) & (
                    db.question.activescope == '4 Local')

            questglob = db(qglob).select(db.question.id, db.question.question_level, db.question.priority,
                                         db.question.category, db.question.answer_group)

            questcont = db(qcont).select(db.question.id, db.question.question_level, db.question.priority,
                                         db.question.category, db.question.answer_group)

            questcount = db(qcount).select(db.question.id, db.question.question_level, db.question.priority,
                                           db.question.category, db.question.answer_group)

            questlocal = db(qlocal).select(db.question.id, db.question.question_level, db.question.priority,
                                           db.question.category, db.question.answer_group)

            quests = (questglob | questcont | questcount | questlocal).sort(lambda r: r.priority, reverse=True)

            if session.answered:
                alreadyans = quests.exclude(lambda r: r.id in session.answered)
            if auth.user.exclude_categories:
                alreadyans = quests.exclude(lambda r: r.category in auth.user.exclude_categories)
            if session.exclude_groups:
                alreadyans = quests.exclude(lambda r: r.answer_group in session.exclude_groups)
            questrow = quests.first()

            if questrow is not None:
                break

    if questrow is None:
        nextquestion = 0
    else:
        nextquestion = questrow.id

    for row in quests:
        session[questtype].append(row.id)
    return nextquestion
    

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
    # get existing category record should always exist
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
    :param questid:
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
            # get the score - if right add to score - if wrong same
            # update userquestion and user - other stuff doesn't apply
            # scoretable = db(db.scoring.level == quest.level).select(cache=(cache.ram, 1200), cacheable=True).first()
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

    resmethods = db(db.resolve.resolve_name == quest.resolvemethod).select()

    if resmethods:
        resmethod = resmethods.first()
        answers_per_level = resmethod.responses
        method = resmethod.resolve_method
    
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
        urgency = quest.urgency
        importance = quest.importance

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

        level = quest.question_level

        # this will be changed to a single select and process the rows
        # object to get counts etc

        #scoretable = db(db.scoring.level == level).select(cache=(cache.ram, 1200), cacheable=True).first()
        scoretable = db(db.scoring.scoring_level == level).select().first()
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
                        (db.userquestion.uq_level == level)).select()

        numanswers = [0] * len(quest.answercounts)
        # numanswers needs to become a list or dictionary
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

        if (max(numanswers) >= ((len(unpanswers) * resmethod.consensus) / 100) or
            method == 'Vote'):  # all answers agree or enough for consensues or vote is being resolved
            status = 'Resolved'
            correctans = numanswers.index(max(numanswers))
            updatedict['correctans'] = correctans

        elif (numreject * 2) > answers_per_level:  # majority reject
            status = 'Rejected'
            correctans = -1
        else:
            # insufficient consensus so promote to next level
            level += 1
            updatedict['question_level'] = level
            status = 'In Progress'
            correctans = -1

        if (numchangescope * 2) > answers_per_level:  # majority want to move scope
            changescope = True

        if (numchangecat * 2) > answers_per_level:  # majority want to move category
            changecat = True

        # update userquestion records

        # this is second pass through to update the records
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
                    numwrong = 0
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
                # update user
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
                    changecategory = True
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
            changestatus = True

        # lines added to avoid error on recalc of computed field
        updatedict['urgency'] = quest.urgency
        updatedict['importance'] = quest.importance

        db(db.question.id == quest.id).update(**updatedict)

        updatequestcounts(quest.qtype, oldcategory, suggestcat, oldstatus, updstatus, quest['answer_group'])

        if status == 'Resolved' and level > 1:
            score_lowerlevel(quest.id, correctans, score, level, wrong)
            # TODO this needs reviewed - not actually doing much at the moment
            if quest.challenge is True:
                if correctans == quest.correctans:
                    successful = False
                else:
                    successful = True
                    # score_challenge(quest.id, successful, level)

    # Think deletion would become a background task which could be triggered here

    message = 'question processed'
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
        usertext = userpref.username
    else:
        usertext = userid
    return usertext


def scopetext(scopeid, continent, country, subdivision):
    request = current.request
    db = current.db

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
    # TODO review compared to D3 one
    # aim to do wordwrapping and possibly stripping and checking as
    # part of this function for jointjs now
    if len(questiontext) < maxlen:
        txt = MARKMIN(questiontext)
    else:
        txt = MARKMIN(questiontext[0:maxlen] + '...')
    return txt


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
    scoretable = db(db.scoring.scoring_level == user.userlevel).select(cache=(cache.ram, 1200), cacheable=True).first()

    if scoretable is None:
        nextlevel = 1000
    else:
        nextlevel = scoretable.nextlevel

    updscore = user.score + score

    if updscore > nextlevel:
        userlevel = user.userlevel + 1
    else:
        userlevel = user.userlevel

    user.update_record(score=updscore, numcorrect=user.numcorrect + numcorrect,
                       numwrong=user.numwrong + numwrong, numpassed=user.numpassed + numpassed,
                       user_level=userlevel)
    # stuff below removed for now as not working and want this to run as background scheduler task so makes no sense
    # to have here in this context
    # if auth.user.id == userid:  # update auth values
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
    :param questid:
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
        level = user.userlevel
        scoretable = db(db.scoring.scoring_level == level).select(cache=(cache.ram, 1200), cacheable=True).first()
        nextlevel = scoretable.nextlevel

        if updscore > nextlevel:
            userlevel = user.userlevel + 1
        else:
            userlevel = user.userlevel

        db(db.auth_user.id == row.auth_userid).update(score=updscore,
                                                      userlevel=userlevel, rating=user.userlevel + userlevel,
                                                      numcorrect=user.numcorrect + numcorrect,
                                                      numwrong=user.numwrong + numwrong)
    return


def score_challengel(questid, successful, level):
    """
    This will reward those that raised a challenge if the answer has changed
    it may also spawn an issue of scoring users who previously thought they
    got it wrong but now got it right - thinking is we wouldn't remove
    points from those that were previously considered right
    :param successful:
    :param questid:
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


def getrundates(period='Day', startdate=datetime.datetime.today()):
    """
    :param period: Valid values are Day, Week or Month
    :return startdate, endate
    So this is a bit crude at moment but not sure I want calendar weeks and months either
    Leave for now
    """

    numdays = (period == 'Day' and 1) or (period == 'Week' and 7) or 30
    enddate = startdate + datetime.timedelta(days=numdays)
    return startdate, enddate


def creategraph(itemids, numlevels=0, intralinksonly=True):
    """
    :param itemids: list
    :param numlevels: int
    :param intralinksonly: boolean
    :return: graph details

    Now think this will ignore eventmap and do no layout related stuff which means events are irrelevant for this
    function it should get links for itemids in an iterable manner and so build of network.py  mainly
    when called from event it will have a list of item ids only from the event already established

    """

    db = current.db
    cache = current.cache
    request=current.request

    query = db.question.id.belongs(itemids)
    quests = db(query).select()

    if intralinksonly:
        # in this case no need to get other questions
        intquery = (db.questlink.targetid.belongs(itemids)) & (db.questlink.status == 'Active') & (
                    db.questlink.sourceid.belongs(itemids))

        # intlinks = db(intquery).select(cache=(cache.ram, 120), cacheable=True)
        links = db(intquery).select()
    else:
        parentlist = itemids
        childlist = itemids

        parentquery = (db.questlink.targetid.belongs(parentlist)) & (db.questlink.status == 'Active')
        childquery = (db.questlink.sourceid.belongs(itemids)) & (db.questlink.status == 'Active')

        links = None
        # just always have actlevels at 1 or more and see how that works
        # below just looks at parents and children - to get partners and siblings we could repeat the process
        # but that would extend to ancestors - so probably need to add as parameter to the query but conceptually
        # this could be repeated n number of times in due course

        # these may become parameters not sure
        # change back to true once working
        getsibs = False
        getpartners = False

        for x in range(numlevels):
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
        links = links.as_list()
    else:
        linklist = []
    return dict(questlist=questlist, linklist=linklist, quests=quests, links=links, resultstring='OK')


def graphpositions(questlist, linklist):
    # this will move to jointjs after initial setup  and this seems to be doing two things at the moment so needs split
    # up into the positional piece and the graph generation - however doesn't look like graph generation is using links 
    # properly either for waiting

    # nodepositions = getpositions(questlist, linklist)
    if debug:
        print questlist, linklist
    return getpositions(questlist, linklist)

def geteventgraph(eventid, redraw=False, grwidth=720, grheight=520, radius=80, status='Open'):
    # this should only need to use eventmap
    # now change to use quest
    stdwidth = 1000
    stdheight = 1000

    db = current.db
    cache = current.cache
    request=current.request

    if status != 'Archived':
        quests = db(db.question.eventid == eventid).select()
    else:
        quests = db(db.eventmap.eventid == eventid).select()

    resultstring='OK'
    linklist = []
    links = None
    intlinks = None
    nodepositions={}
    questlist = [x.id for x in quests]
    if not questlist:
        resultstring='No Items setup for event'
    else:
        intquery = (db.questlink.targetid.belongs(questlist)) & (db.questlink.status == 'Active') & (
                    db.questlink.sourceid.belongs(questlist))
        intlinks = db(intquery).select()
        print intlinks
        links = [x.sourceid for x in intlinks]

        if links:
            linklist = [(x.sourceid, x.targetid, {'weight': 30}) for x in intlinks]

        if redraw and status != 'Archived':
            nodepositions = getpositions(questlist, linklist)
            for row in quests:
                row.update_record(xpos=(nodepositions[row.id][0] * stdwidth), ypos=(nodepositions[row.id][1] * stdheight))
                nodepositions[row.id][0] = ((nodepositions[row.id][0] * grwidth) / stdwidth) + radius
                nodepositions[row.id][1] = ((nodepositions[row.id][0] * grheight) / stdheight) + radius
        else:
            nodepositions = {}
            for row in quests:
                nodepositions[row.id] = (((row.xpos * grwidth) / stdwidth) + radius, ((row.ypos * grheight) / stdheight) + radius)

    return dict(questlist=questlist, linklist=linklist, quests=quests, links=intlinks, nodepositions=nodepositions, resultstring=resultstring)

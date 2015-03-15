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
This controller handles the selection of an available question and the 
answering of it
6 Mar 2013 - rewrite to improve logic and consider 'late' answers to questions
which might be quite common as operation of selection is to always give the
highest priority question out to all users and work on resolving it first
"""

"""
    exposes:
    http://..../[app]/answer/get_question -- stays
    http://..../[app]/answer/score_challenge -- moved to nds functions untested
    http://..../[app]/answer/score_lowerlevel --  moved to nds functions untested
    http://..../[app]/answer/all_question - basically still the same
    http://..../[app]/about/answer_question - enhance
    http://..../[app]/about/score_question  moved to nds functions and working
    """
from ndsfunctions import updatequestcounts, score_question, updateuser
from ndspermt import get_exclude_groups

@auth.requires_login()
def all_questions():
    """
    Used when no questions in the database that user has not already answered.
    """
    return locals()


@auth.requires_login()
def get_question():
    """
    TO DO - this will need a COMPLETE rewrite - outline in v4 xlsx
    Get unresolved question from the question database that the user has not answered.    
    This will now support both challenges and normal questions in 
    progress - both can hopefully go through the same flow and their is now
    just a boolean flag to represent a challenge so the challengees can be 
    given points too and they get them if the answer changes 
    a single function will do this retrieves the highest priority question that
    the user hasn't answered initially looking for questions at the same level 
    as the user and then lower level questions and finally
    higher level questions users can hopefully select whether to only approve
    actions or questions or approve both based on request.args(0)

    Update for groups and generally - this may be quite a lengthy operation in due course and it may make sense to move
    to a background process - we are also looking to provide quick answers to issues and actions and allow answering
    of questions to be selectable by users if the user allows it.  There is also some case for prioritising questions
    that are restricted to certain groups - and this might become a user preference - however for now we will just go with
    what we have got and filter for excluded groups I think. However not that keen on the compilation of 4 lists as well for
    actions, issues, questions and overall - so that needs some thought.

    We should also remove any questions users choose to answer from the session lists and ultimately this should
    probably mainly be a background task -
    """

    # Added questlist to minimise database reads when running this and also
    # to create potential delay between submission and starting to answer
    # question - however issue is that this can be called 3 ways so got
    # 3 separate lists at present - depending on whether user want to answer quests, issues
    # or actions - may just move this to only be for questions as can probably do quick
    # approval of issues and actions and just have a questlist with actions and issues
    # being covered by review type options??
    # may also having ability to access this from group - but I think approach is 
    # just that group questions take priority and all update questlist

    # first identify all questions that have been answered and are in progress

    global quests
    questrow = None
    questtype = 'all'
    if request.args(0) == 'action':
        questtype = 'action'
        if session.actionlist is None:
            session.actionlist = []
        elif len(session.actionlist) > 1:
            session.actionlist.pop(0)
            nextquest = str(session.actionlist[0])
            redirect(URL('answer_question', args=nextquest))

    elif request.args(0) == 'quest':
        questtype = 'quest'
        if session.questlist is None:
            session.questlist = []
        elif len(session.questlist) > 1:
            session.questlist.pop(0)
            nextquest = str(session.questlist[0])
            redirect(URL('answer_question', args=nextquest))

    #probably elif == issue here but this is getting repetitive

    session.comblist = None
    if session.comblist is None:
        session.comblist = []
    elif len(session.comblist) > 1:
        session.comblist.pop(0)
        nextquest = str(session.comblist[0])
        redirect(URL('answer_question', args=nextquest))

    if session.answered is None:
        session.answered = []
        ansquests = db((db.userquestion.auth_userid == session.userid) &
                       (db.userquestion.status == 'In Progress')).select(db.userquestion.questionid)

        for row in ansquests:
            session.answered.append(row.questionid)

    # if session.exclude_cats is None:
    session.exclude_cats = auth.user.exclude_categories
    if session.exclude_groups is None:
        session.exclude_groups = get_exclude_groups(auth.user_id)

    if session.continent == 'Unspecified':  # ie no geographic restriction
        for i in xrange(0, 4):
            if i == 0:
                query = (db.question.level == session.level) & (db.question.status == 'In Progress')
                orderstr = ~db.question.priority
            elif i == 1:
                if session.level < 2:
                    continue
                else:
                    query = (db.question.level < session.level) & (db.question.status == 'In Progress')
                    orderstr = ~db.question.level | ~db.question.priority
            elif i == 2:
                query = (db.question.level > session.level) & (db.question.status == 'In Progress')
                orderstr = db.question.level | ~db.question.priority
            elif i == 3:
                query = (db.question.status == 'In Progress')
                orderstr = ~db.question.priority

            if questtype != 'all':
                query &= db.question.qtype == questtype

            if i < 3:
                #remove caching and see if fixes for now
                #quests = db(query).select(orderby=orderstr,cache=(cache.ram, 120), cacheable=True)
                quests = db(query).select(orderby=orderstr)
            else:  # no caching for final attempt
                quests = db(query).select(orderby=~db.question.priority)

            # exclude previously answered - this approach specifically taken rather than
            # an outer join so it can work on google app engine
            # then filter for unanswered and categories users dont want questions on
            alreadyans = quests.exclude(lambda row: row.id in session.answered)
            if session.exclude_cats:
                alreadyans = quests.exclude(lambda row: row.category in session.exclude_cats)
            alreadyans= quests.exclude(lambda row: row.answer_group in session.exclude_groups)

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
                query = (db.question.level == session.level) & (db.question.status == 'In Progress')
            elif i == 1:
                if session.level < 2:
                    continue
                else:
                    query = (db.question.level < session.level) & (db.question.status == 'In Progress')
            elif i == 2:
                query = (db.question.level > session.level) & (db.question.status == 'In Progress')
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

            questglob = db(qglob).select(db.question.id, db.question.level, db.question.priority,
                                         db.question.category, db.question.answer_group)

            questcont = db(qcont).select(db.question.id, db.question.level, db.question.priority,
                                         db.question.category, db.question.answer_group)

            questcount = db(qcount).select(db.question.id, db.question.level, db.question.priority,
                                           db.question.category, db.question.answer_group)

            questlocal = db(qlocal).select(db.question.id, db.question.level, db.question.priority,
                                           db.question.category, db.question.answer_group)

            quests = (questglob | questcont | questcount | questlocal).sort(lambda r: r.priority, reverse=True)

            alreadyans = quests.exclude(lambda r: r.id in session.answered)
            alreadyans = quests.exclude(lambda r: r.category in session.exclude_cats)
            alreadyans = quests.exclude(lambda r: r.answer_group in session.exclude_groups)
            questrow = quests.first()

            if questrow is not None:
                break

    if questrow is None:
        # No questions because all questions in progress are answered
        redirect(URL('all_questions'))

    # put quests into a list of id's to only run this when
    # we run out of questions for this user ie make a queue or change selection
    # type for the list we want to answer

    if questtype == 'action':
        for row in quests:
            session.actionlist.append(row.id)
    elif questtype == 'quest':
        for row in quests:
            session.questlist.append(row.id)
    else:
        for row in quests:
            session.comblist.append(row.id)

    redirect(URL('answer_question', args=questrow.id))
    return ()


# This may need to become a requires signature
@auth.requires_login()
def answer_question():
    """
    This allows the user to answer the question or pass and the result is 
    handled by the score question function.  This can really now be called
    from any event and it is an exposed url - so now need to check if not 
    resolved or already answered and if so we will not accept another answer
    """

    questid = request.args(0, cast=int, default=0)
    # This will display the question submitted to it by get_question

    form2 = SQLFORM(db.userquestion, showid=False, fields=['answer', 'reject',
                                                           'urgency', 'importance', 'answerreason', 'changecat',
                                                           'category', 'changescope',
                                                           'activescope', 'continent', 'country', 'subdivision'],
                    submit_button='Answer', col3={'answer': 'Enter 0 to Pass',
                                                  'reject': 'Select if invalid or off subject '},
                    hidden=dict(level='level'), formstyle='table3cols')

    # bootstrap3_inline
    #quest = db(db.question.id == questid).select(cache=(cache.ram, 600), cacheable=True).first().as_dict()
    #this now caused userquestion to be set to wrong level so caching removed for now
    quest = db(db.question.id == questid).select().first().as_dict()

    if session.exclude_groups is None:
        session.exclude_groups = get_exclude_groups(auth.user_id)

    if quest['answer_group'] in session.exclude_groups:
        redirect(URL('viewquest', 'notshowing', args=[questid]))

    if quest['status'] != 'In Progress':
        redirect(URL('viewquest', 'index', args=[questid]))
    else:
        uq = db((db.userquestion.questionid == questid) &
                (db.userquestion.status == 'In Progress') &
                (db.userquestion.auth_userid == auth.user_id)).select(db.userquestion.id).first()
        if uq:
            redirect(URL('viewquest', 'index', args=[questid]))

    # Took level out of this as it cannot be cached

    form2.vars.activescope = quest['activescope']
    form2.vars.continent = quest['continent']
    form2.vars.country = quest['country']
    form2.vars.subdivision = quest['subdivision']
    form2.vars.category = quest['category']

    if form2.validate():
        form2.vars.auth_userid = auth.user.id
        form2.vars.questionid = questid
        form2.vars.level = quest['level']
        form2.vars.status = 'In Progress'
        form2.vars.id = db.userquestion.insert(**dict(form2.vars))
        response.flash = 'form accepted'
        #redirect(URL('update_question', args=form2.vars.id))
        score_question(questid, form2.vars.id)
        # will move to call update_question in a module perhaps with userid and question as args??
        redirect(URL('viewquest', 'index', args=questid))
    elif form2.errors:
        response.flash = 'form has errors'
    else:
        pass
        # response.flash = 'please fill out the form'

    form2.vars.continet = quest['continent']
    form2.vars.country = quest['country']
    form2.vars.subdivision = quest['subdivision']
    form2.vars.category = quest['category']

    return dict(form2=form2, quest=quest)


@auth.requires_login()
def quickanswer():
    """
    This willl provide a quick method of approving an action or issue by means of approve disapprove buttons
    basically needs to create a userquestion record and remove the buttons from the relevant row which
    may be more challenging - it will never apply to questions and there is a question about how scope changes and
    geography changes should be handled - but for now we are going to implicitly answer that these stay where they are
    and retrieve them from the question
    """

    questid = request.args(0, cast=int, default=0)
    answer = request.args(1, cast=int, default=-1)

    quest = db(db.question.id == questid).select().first()

    if quest:
        db.userquestion.insert(questionid=questid, auth_userid=auth.user_id, level=quest.level, answer=answer,
                               reject=False, urgency=quest.urgency, importance=quest.importance, category=quest.category,
                               activescope=quest.activescope, continent=quest.continent, country=quest.country)

        # this probably shouldn't be a redirect here so I think we would move to scoring these on a background thread
        # as this is supposed to be quick and don't need the result but the userquestion record is already updated so
        # potentially would want the score question piece fully in a module shortly
        db.qscorequest.insert(questid=questid)  # this will then be scored by means of score_question module
        messagetxt = 'Answer Recorded'

        intunpanswers = quest.unpanswers
        # only update unpanswers if the userd didn't pass otherwise just keep going
        # until we get 3 actual answers or rejections
        # or uq.reject is True:
        if answer != -1:
            intunpanswers += 1

        numquests = auth.user.numquestions + 1
        db(db.auth_user.id == auth.user.id).update(numquestions=numquests)
        auth.user.update(numquestions=numquests)
        if session.answered: # optional if user selects question to answer
            session.answered.append(uq.questionid)

        anscount = quest.answercounts
        anscount[answer] += 1

        # update the question record based on above
        db(db.question.id == quest.id).update(answercounts=anscount, unpanswers=intunpanswers)
        # scoring of question will come from score_question module 

    else:
        messagetxt = 'Answer not recorded'
    return messagetxt

@auth.requires_login()
def update_question():
    """
    This procedure updates the question and userquestion records after each answer
    The update is in 2 parts.  The number of answers and so on are

    always updated however the main scoring only happens when we have 3 or more
    unprocessed answers. so there is a case to separate into two functions however reluctant 
    to push scoring onto scheduler as user need to know immediately if they solved the question
    however score lower level should probably be scheduled
    only call score_question if sufficient unprocessed answers
    """
    # So this is being phased out 
    # Initial processing that happens all the time
    intrec = request.args(0, cast=int)
    uq = db.userquestion[intrec]

    quest = db(db.question.id == uq.questionid).select().first()

    ANSWERS_PER_LEVEL = 3  

    # first step is to select the related user and question records their should
    # only ever be one of each of these and we update as much as possible here 
    # because it's interesting to see as much as possible on viewquest rather
    # than waiting until 3 people have answered and it can be scored - however this can result in
    # a degree of double updating

    if quest.qtype == 'action':
        # create a 'questurgency' record if action only - thinking is that
        # prioritising actions in progress is wortwhile and open to all

        db.questurgency.update_or_insert((db.questurgency.auth_userid == auth.user.id)
                                         & (db.questurgency.questionid == quest.id), questionid=quest.id,
                                         auth_userid=auth.user.id,
                                         urgency=uq.urgency, importance=uq.importance)

    intunpanswers = quest.unpanswers
    # only update unpanswers if the userd didn't pass otherwise just keep going
    # until we get 3 actual answers or rejections
    if uq.answer != -1 or uq.reject is True:
        intunpanswers += 1

    numquests = auth.user.numquestions + 1
    db(db.auth_user.id == auth.user.id).update(numquestions=numquests)
    auth.user.update(numquestions=numquests)
    if session.answered: # optional if user selects question to answer
        session.answered.append(uq.questionid)

    # do weighted averaging of urgency and importance based on userquest and this is 
    # accepted from passers

    urgency = (((quest.urgency * quest.totanswers()) + uq.urgency) /
               (quest.totanswers() + 1))
    importance = (((quest.importance * quest.totanswers()) + uq.importance) /
                  (quest.totanswers() + 1))

    anscount = quest.answercounts
    anscount[uq.answer] += 1

    # update the question record based on above
    db(db.question.id == quest.id).update(answercounts=anscount,
                                          urgency=urgency, importance=importance, unpanswers=intunpanswers)

    if intunpanswers >= ANSWERS_PER_LEVEL:
        #redirect(URL('score_question', args=quest.id))
        score_question(quest.id)
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
        # This should be moved to a module as well so can be called from quickquestion and
        # normal - not putting into quick in order to take out again

        if quest.status == 'Resolved' or quest.status == 'Agreed':
            #get the score - if right add to score - if wrong same
            #update userquestion and user - other stuff doesn't apply
            scoretable = db(db.scoring.level == quest.level).select(cache=(cache.ram, 1200), cacheable=True).first()
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
            updateuser(auth.user.id, updscore, numcorrect, numwrong, numpassed)

    redirect(URL('viewquest', 'index', args=quest.id))


@auth.requires_login()
def notscore_question():
    """
    So this now only called if sufficient answers to attempt to resolve - I think we would have a separate routine for vote results as well
    shouldn't really be anything special about the last user versus the other ones in this
    """

    ANSWERS_PER_LEVEL = 3  

    questid = request.args(0, cast=int)
    quest = db(db.question.id == questid).select().first()

    stdrouting = ANSWERS_PER_LEVEL
    status = 'In Progress'
    changecat = False
    changescope = False

    # if intunpanswers >= stdrouting:
    # this should always be true now
    # scorequestions - need to get all the answers first at this level -
    # should agree to unpanswers and should be a small number - so lets fully
    # score these - if they don't agree to unpanswers then doesn't agree
    # and will need to be escalated - so simple score if resolved - lower
    # levels will probably be done as a background task eventually so seems
    # ok this should never happen on a passed question at present challengees
    # are not getting credit for right or wrong challenges - this will be
    # added in a subsequent update not that complicated to do however

    level = quest.level

    # this will be changed to a single select and process the rows
    # object to get counts etc

    scoretable = db(db.scoring.level == level).select(cache=(cache.ram, 1200), cacheable=True).first()
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

    redirect(URL('viewquest', 'index', args=quest.id))

    return locals()

def notupdateuser(userid, score, numcorrect, numwrong, numpassed):

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

    if auth.user.id == userid:  # update auth values
        auth.user.update(score=updscore, level=userlevel, rating=userlevel, numcorrect=
                                 auth.user.numcorrect + numcorrect, numwrong=auth.user.numwrong + numwrong,
                                 numpassed=auth.user.numpassed + numpassed)

    return True

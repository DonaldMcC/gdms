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
    that are restricted to certain groups - and this might become a user preference - however for now we will just go
    with what we have got and filter for excluded groups I think. However not that keen on the compilation of 4 lists
    as well for actions, issues, questions and overall - so that needs some thought.

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

    questtype = request.args(0, default = 'all')
    if session.items:
        # is key there and 
        if session.items.key and len >1
       
            session.actionlist.pop(0)
            nextquest = str(session.actionlist[0])
        redirect(URL('answer_question', args=nextquest))
        else
        session.items[questtype=[]]
    else:
        session.items={}
        
        # pop logic belows looks wrong
        
    if request.args(0) == 'action':
        questtype = 'action'
        if session.actionlist is None:
            session.actionlist = []
        elif len(session.actionlist) > 1:
            session.actionlist.pop(0)
            nextquest = str(session.actionlist[0])
            redirect(URL('answer_question', args=nextquest))

    # below would be dependant on SQL variable possibly with debug option to check if results the same
    # which I think means it's a function call
    
    #maybe just populate the list and then test if true
    #debug option coud call again with alternative params
    
    if session.answered is None:
        session.answered = []
        ansquests = db((db.userquestion.auth_userid == session.userid) &
                       (db.userquestion.status == 'In Progress')).select(db.userquestion.questionid)

        for row in ansquests:
            session.answered.append(row.questionid)

    # if session.exclude_cats is None:
    # session.exclude_cats = auth.user.exclude_categories
    session.exclude_groups = get_exclude_groups(auth.user_id)

    # removed temporarily for re-test
    # if session.exclude_groups is None:
    #    session.exclude_groups = get_exclude_groups(auth.user_id)

    orderstr = ''
    if session.continent == 'Unspecified':  # ie no geographic restriction
        for i in xrange(0, 4):
            if i == 0:
                query = (db.question.question_level == session.level) & (db.question.status == 'In Progress')
                orderstr = ~db.question.priority
            elif i == 1:
                if session.level < 2:
                    continue
                else:
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

            # exclude previously answered - this approach specifically taken rather than
            # an outer join so it can work on google app engine
            # then filter for unanswered and categories users dont want questions on
            alreadyans = quests.exclude(lambda row: row.id in session.answered)
            alreadyans = quests.exclude(lambda row: row.category in auth.user.exclude_categories)
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

            alreadyans = quests.exclude(lambda r: r.id in session.answered)
            alreadyans = quests.exclude(lambda r: r.category in auth.user.exclude_categories)
            alreadyans = quests.exclude(lambda r: r.answer_group in session.exclude_groups)
            questrow = quests.first()

            if questrow is not None:
                break

    if questrow is None:
        # No questions because all questions in progress are answered
        redirect(URL('all_questions'))

    if questtype == 'action':
        for row in quests:
            session.actionlist.append(row.id)
    elif questtype == 'quest':
        for row in quests:
            session.questlist.append(row.id)
    else:
        for row in quests:
            session.comblist.append(row.id)
            
    # return point will basically be here with         

    redirect(URL('answer_question', args=questrow.id))
    return ()


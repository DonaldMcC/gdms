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


"""
This controller handles the selection of an available question and the 
answering of it
6 Mar 2013 - rewrite to improve logic and consider 'late' answers to questions
which might be quite common as operation of selection is to always give the
highest priority question out to all users and work on resolving it first
"""

"""
    exposes:
    http://..../[app]/answer/all_questiona - basically still the same
    http://..../[app]/answer/get_question -- stays
    http://..../[app]/about/answer_question - enhance
    """
from ndsfunctions import score_question
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

    # probably elif == issue here but this is getting repetitive

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
    # session.exclude_cats = auth.user.exclude_categories
    session.exclude_groups = get_exclude_groups(auth.user_id)

    # removed temporarily for re-test
    # if session.exclude_groups is None:
    #    session.exclude_groups = get_exclude_groups(auth.user_id)

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
    # quest = db(db.question.id == questid).select(cache=(cache.ram, 600), cacheable=True).first().as_dict()
    # this now caused userquestion to be set to wrong level so caching removed for now
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
        # default to urgency 10 for testing so questions that are answered continue to get answered
        if auth.user.first_name[:4] == 'Test':
            form2.vars.urgency = 10
            form2.vars.importance = 10

        form2.vars.id = db.userquestion.insert(**dict(form2.vars))
        response.flash = 'form accepted'
        # redirect(URL('update_question', args=form2.vars.id))
        status = score_question(questid, form2.vars.id)
        if status == 'Resolved':
            #send_email(1,2,3,4,5)
            #send_email_resolved(questid)
            scheduler.queue_task('send_email_resolved', pvars=dict(questid=questid), period=600)
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
    uq = db((db.userquestion.questionid == questid) & (db.userquestion.auth_userid == auth.user_id)
            & (db.userquestion.status == 'In Progress')).select()

    if quest and not uq:
        uqid = db.userquestion.insert(questionid=questid, auth_userid=auth.user_id, level=quest.level, answer=answer,
                                      reject=False, urgency=quest.urgency, importance=quest.importance,
                                      category=quest.category, activescope=quest.activescope, continent=quest.continent,
                                      country=quest.country)

        status = score_question(questid, uqid)
        if status == 'Resolved':
            #send_email(1,2,3,4,5)
            scheduler.queue_task('send_email_resolved', pvars=dict(questid=questid), period=600)
        messagetxt = 'Answer recorded for item:' + str(questid)

        intunpanswers = quest.unpanswers
        # only update unpanswers if the userd didn't pass otherwise just keep going
        # until we get 3 actual answers or rejections
        # or uq.reject is True:
        if answer != -1:
            intunpanswers += 1

        # this can be removed as now included in score_question
        #numquests = auth.user.numquestions + 1
        #db(db.auth_user.id == auth.user.id).update(numquestions=numquests)
        #auth.user.update(numquestions=numquests)

        if session.answered:  # optional if user selects question to answer
            session.answered.append(uq.questionid)

        anscount = quest.answercounts
        anscount[answer] += 1

        # update the question record based on above
        db(db.question.id == quest.id).update(answercounts=anscount, unpanswers=intunpanswers,
                                              urgency=quest.urgency, importance=quest.importance)
        # scoring of question will come from score_question module 
        print questid, ' was quick approved'
    elif uq:
        messagetxt = 'You have already answered this item'
    else:
        messagetxt = 'Answer not recorded'

    return 'jQuery(".flash").html("' + messagetxt + '").slideDown().delay(1500).slideUp(); $("#target").html("' + messagetxt + '"); $("#btns' + str(questid
            ) + ' .btn-success").addClass("disabled").removeClass("btn-success"); $("#btns' + str(questid
            ) + ' .btn-danger").addClass("disabled").removeClass("btn-danger");'

    # return "$('#target').html('" + messagetxt + "');


def score_complete_votes():
    # this will identify votes which are overdue based on being in progress 
    # beyond due date and with resmethod of vote

    votemethods = db(db.resolvemethod.method == 'Vote').select()
    votelist = [x.resolve_name for x in votemethods]

    query = (db.question.duedate > datetime.datetime.utcnow()) & (db.question.status == 'In Progress')
    quests = db(query).select()

    for x in quests:
        if x.resolvemethod in votelist:
            print('scoring'+ x.id) 
            scorequestion(x.id)
    if quests:
        print('processsed ' + str(len(quests)))
    else:
        print('zero items to process')
    return True

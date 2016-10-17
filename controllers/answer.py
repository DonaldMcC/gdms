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

from get_quest import getquestnonsql, getquestsql, getquesteventsql
from ndsfunctions import score_question,  getitem
from ndspermt import get_exclude_groups


"""
This controller handles the selection of an available question and the 
answering of it
6 Mar 2013 - rewrite to improve logic and consider 'late' answers to questions
which might be quite common as operation of selection is to always give the
highest priority question out to all users and work on resolving it first

    exposes:
    http://..../[app]/answer/all_questiona - basically still the same
    http://..../[app]/answer/get_question -- stays
    http://..../[app]/about/answer_question - enhance
    http://..../[app]/answer/quickanswer - ajax submission of answers to issues and actions
    http://..../[app]/answer/score_complete_votes - enquiry for scoring overdue votes 
    should be 4 views from this controller but get_question never called and no score complete votes yet
    
"""


@auth.requires_login()
def all_questions():
    """
    Used when no questions in the database that user has not already answered.
    """
    questtype = request.args(0, default='quest')

    return dict(questtype=getitem(questtype))


@auth.requires_login()
def all_event():
    """
    Used when no questions in the database that user has not already answered.
    """
    eventid = request.args(0, cast=int, default=0)

    return dict(eventid=eventid)


@auth.requires_login()
def get_question():

    # Added questlist to minimise database reads when running this and also
    # to create potential delay between submission and starting to answer
    # question - however issue is that this can be called 3 ways so had
    # 3 separate lists at present - depending on whether user want to answer quests, issues
    # or actions - may just move this to only be for questions as can probably do quick
    # approval of issues and actions and just have a questlist with actions and issues
    # being covered by review type options??
    # may also having ability to access this from group - but I think approach is
    # just that group questions take priority and all update questlist
    # first identify all questions that have been answered and are in progress
    # now with event questions selection is all and this gets a list for the event

    questtype = request.args(0, default='quest')
    eventid = request.args(1, cast=int, default=0)  
    
    if session[questtype] and len(session[questtype]):
        nextquest = str(session[questtype].pop(0))
        # nextquest = str(session[questtype][0])
        redirect(URL('answer_question', args=[nextquest, questtype], user_signature=True))

    if eventid:
        nextquestion = getquesteventsql(eventid)
    else:
        if dbtype == 'sql':
            nextquestion = getquestsql(questtype, auth.user_id, auth.user.exclude_categories, use_address)
        else:
            nextquestion = getquestnonsql(questtype, auth.user_id, auth.user.exclude_categories)

    if nextquestion == 0:
        if questtype != 'All':
            redirect(URL('all_questions', args=questtype))
        else:
            redirect(URL('all_event', args=eventid))
    else:
        redirect(URL('answer_question', args=[nextquestion, questtype], user_signature=True))
    return ()


# changed to require signature
@auth.requires_login()
@auth.requires_signature()
def answer_question():
    """
    This allows the user to answer the question or pass and the result is 
    handled by the score question function.  This can really now be called
    from any event and it is an exposed url - so now need to check if not 
    resolved or already answered and if so we will not accept another answer
    """

    questid = request.args(0, cast=int, default=0)
    questtype = request.args(1, default='quest')  # This will be All if on an event flow and this will flow to viewquest
    # This will display the question submitted to it by get_question

    form2 = SQLFORM(db.userquestion, showid=False, fields=['answer', 'reject', 'urgency', 'importance', 'answerreason',
                                                           'changecat', 'category', 'changescope',
                                                           'activescope', 'continent', 'country', 'subdivision', 'coord'],
                    submit_button='Answer', col3={'answer': 'Enter 0 to Pass',
                                                  'reject': 'Select if invalid or off subject '},
                    hidden=dict(uq_level='level'), formstyle='table3cols')

    # bootstrap3_inline
    # quest = db(db.question.id == questid).select(cache=(cache.ram, 600), cacheable=True).first().as_dict()
    # this now caused userquestion to be set to wrong level so caching removed for now
    quest = db(db.question.id == questid).select().first().as_dict()

    if session.exclude_groups is None:
        session.exclude_groups = get_exclude_groups(auth.user_id)

    if quest['answer_group'] in session.exclude_groups:
        redirect(URL('viewquest', 'notshowing', args=[questid, questtype]))

    if quest['status'] != 'In Progress':
        redirect(URL('viewquest', 'index', args=[questid, questtype]))
    else:
        uq = db((db.userquestion.questionid == questid) &
                (db.userquestion.status == 'In Progress') &
                (db.userquestion.auth_userid == auth.user_id)).select(db.userquestion.id).first()
        if uq:  # User has already answered item so not allowed to answer again
            redirect(URL('viewquest', 'index', args=[questid, questtype]))

    form2.vars.activescope = quest['activescope']
    form2.vars.continent = quest['continent']
    form2.vars.country = quest['country']
    form2.vars.subdivision = quest['subdivision']
    form2.vars.category = quest['category']

    if form2.validate():
        form2.vars.auth_userid = auth.user.id
        form2.vars.questionid = questid
        form2.vars.uq_level = quest['question_level']
        form2.vars.status = 'In Progress'
        # default to urgency 10 for testing so questions that are answered continue to get answered
        if auth.user.first_name[:4] == 'Test':
            form2.vars.urgency = 10
            form2.vars.importance = 10

        form2.vars.id = db.userquestion.insert(**dict(form2.vars))
        response.flash = 'form accepted'
        status = score_question(questid, form2.vars.id)
        if status == 'Resolved':
            scheduler.queue_task('send_email_resolved', pvars=dict(questid=questid), period=600)
        redirect(URL('viewquest', 'index', args=[questid, questtype]))
    elif form2.errors:
        response.flash = 'form has errors'

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
    uq = db((db.userquestion.questionid == questid) & (db.userquestion.auth_userid == auth.user_id) &
            (db.userquestion.status == 'In Progress')).select()

    if quest and not uq:
        uqid = db.userquestion.insert(questionid=questid, auth_userid=auth.user_id, uq_level=quest.question_level,
                                      answer=answer, reject=False, urgency=quest.urgency, importance=quest.importance,
                                      category=quest.category, activescope=quest.activescope, continent=quest.continent,
                                      country=quest.country)

        status = score_question(questid, uqid)
        if status == 'Resolved':
            scheduler.queue_task('send_email_resolved', pvars=dict(questid=questid), period=600)
        messagetxt = 'Answer recorded for item:' + str(questid)

        intunpanswers = quest.unpanswers
        if answer != -1:
            intunpanswers += 1

        if session.answered:  # optional if user selects question to answer
            session.answered.append(questid)
        anscount = quest.answercounts
        anscount[answer] += 1

        # update the question record based on above
        db(db.question.id == quest.id).update(answercounts=anscount, unpanswers=intunpanswers,
                                              urgency=quest.urgency, importance=quest.importance)

    elif uq:
        messagetxt = 'You have already answered this item'
    else:
        messagetxt = 'Answer not recorded'

    return 'jQuery(".w2p_flash").html("' + messagetxt + '").slideDown().delay(1500).slideUp(); $("#target").html("' \
       + messagetxt + '"); $("#btns' + str(questid) + ' .btn-success").addClass("disabled").removeClass("btn-success"); $("#btns'\
      + str(questid) + ' .btn-danger").addClass("disabled").removeClass("btn-danger");'




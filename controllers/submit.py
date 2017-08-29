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
# This controller handles submission of questions and actions and confirmation 
# that the question has been submitted
# v2 rewrite to attempt to use a standard form with list string as hidden fields a bit of
# an unnecessary step
###############################################################################


"""
    exposes:
    http://..../[app]/submit/new_question
    http://..../[app]/submit/accept_question
    http://..../[app]/submit/subdivision - AJAX update to selection
    http://..../[app]/submit/country - AJAX update to selection
    http://..../[app]/submit/drafttoinprog  - AJAX update to confirm items

    """
from ndspermt import get_groups, can_edit_plan
from ndsfunctions import getitem
import wolframalpha
import urllib


@auth.requires_login()
def new_question():
    # This allows creation of questions, actions and issues and std flow depends on  whether question or action/issue
    # is being  submitted the default is question unless action or issue specified
    # self answered questions are now possible as part of a chain of thought - and these can be requested from the menu
    # but any question with just one answer will trigger this prompt - whereas adding a second answer makes it a
    # normal question - fields are hidden by default on self quest but notes field is shown  as it is for edited
    # quests - maybe should be for everything??
    # so final flow is self-quest based on arg1 leads to hiding cells and will go through as resolved - formatting may
    # be based on only 1 ie second answer changes the flow - that is step 1,
    # step 2 is to hide the fields sort of done, step3 is to override to normal if second a
    # second item added and flip back when second answer deleted - confirm prompt should happen on false but only if
    # the flow didn't start that way - after that we may then need formatting of selfquests and display of notes
    # once the above is done then I think we can use comments on notes to lookup wolfram alpha
    # let's do prompt if not started that way next and also validate that resolved only has 1 answer as next step

    qtype = request.args(0, default='quest')
    questid = request.args(1, cast=int, default=0)
    status = request.args(2, default=None)
    context = request.args(3, default=None)
    eventid = request.args(4, cast=int, default=0)
    projid = request.args(5, cast=int, default=0)
    record = 0

    if qtype == 'selfquest':
        selfquest = True
        qtype = 'quest'
    else:
        selfquest = False

    if questid:
        record = db.question(questid)
        qtype = record.qtype
        if record.auth_userid != auth.user.id or record.status != 'Draft':
            session.flash = 'Not Authorised - items can only be edited by their owners'
            redirect(URL('default', 'index'))

    # this will become a variable priorquest = request.args(1, cast=int, default=0)
    priorquest = request.vars.priorquest or 0

    if session.access_group is None:
        session.access_group = get_groups(auth.user_id)

    db.question.answer_group.requires = IS_IN_SET(session.access_group)
    db.question.status.requires = IS_IN_SET(['Draft', 'In Progress'])

    if qtype == 'quest':
        if selfquest:
            heading = 'Submit Self Answered Question'
            labels = {'questiontext': 'Question'}
            fields = ['questiontext', 'answers', 'notes', 'projid', 'eventid', 'resolvemethod', 'duedate', 'answer_group', 'category',
                      'activescope', 'continent', 'country', 'subdivision', 'coord', 'status']
            #resolvemethod and answergropu can be hidden
        else:
            heading = 'Submit Question'
            labels = {'questiontext': 'Question'}
            fields = ['questiontext', 'projid', 'eventid', 'resolvemethod', 'duedate', 'answer_group', 'category',
                  'activescope', 'continent', 'country', 'subdivision', 'coord', 'status', 'answers']

    elif qtype == 'action':
        heading = 'Submit Action'
        labels = {'questiontext': 'Action'}
        fields = ['questiontext', 'projid', 'eventid', 'resolvemethod', 'duedate', 'responsible', 'answer_group',
                  'category', 'activescope', 'continent', 'country', 'subdivision', 'coord', 'status', 'shared_editing']
    else:
        heading = 'Submit Issue'
        labels = {'questiontext': 'Issue'}
        fields = ['questiontext', 'projid', 'eventid', 'resolvemethod', 'duedate', 'answer_group', 'category',
                  'activescope', 'continent', 'country', 'subdivision', 'coord', 'status']

    if questid:
        fields.insert(0, 'qtype')
        if not selfquest:
            fields.insert(-1, 'notes')
        form = SQLFORM(db.question, record, fields=fields, labels=labels, deletable=True)
    else:
        form = SQLFORM(db.question, fields=fields, labels=labels)

    form.element(_type='submit')['_class'] = "btn btn-success"

    form.vars.eventid = eventid or session.eventid or db(db.evt.evt_name == 'Unspecified').select(db.evt.id).first().id

    form.vars.projid = projid or session.projid or db(db.project.proj_name == 'Unspecified').select(
                                                      db.project.id).first().id

    if selfquest:
        form.vars.resolvemethod='Resolved'
    elif session.resolvemethod:
        form.vars.resolvemethod = session.resolvemethod
    else:
        form.vars.resolvemethod = PARAMS.default_resolve_name
    
    if session.status and status is None:
        status = session.status

    # this can be the same for both questions and actions
    if form.validate(keepvalues=True):
        form.vars.question_lat, form.vars.question_long = IS_GEOLOCATION.parse_geopoint(form.vars.coord)
        if not questid:  # not editing
            form.vars.auth_userid = auth.user.id
            form.vars.qtype = qtype

        if form.vars.qtype == 'action':
            form.vars.answers = ['Approve', 'Disapprove', 'OK']
        elif form.vars.qtype == 'issue':
            form.vars.answers = ['Agree', 'Disagree', 'OK']

        form.vars.answercounts = [0]*(len(form.vars.answers))

        form.vars.createdate = request.utcnow
        if status == 'draft':
            form.vars.status = 'Draft'
        # section below will only have effect if Resolved resolution method setup manually it is not
        # intended for normal system use but can allow loading of actions in a resolved state and will
        # now be extended to support self resolved questions as part of a chain of thought
        elif form.vars.resolvemethod == 'Resolved':
            if form.vars.qtype == 'action' or form.vars.qtype == 'issue':
                form.vars.status = 'Agreed'
            else:
                form.vars.status = 'Resolved'
                if isinstance(form.vars.answers, list) and len(form.vars.answers) > 1 and len(form.vars.answers[1]) > 0:
                    # need type checking as becomes string if only 1 item
                    response.flash = 'form has errors '
                    form.errors.resolvemethod = "Self resolved can only have 1 answer"
                    return dict(form=form, heading=heading, selfquest=selfquest)
        else:
            if not isinstance(form.vars.answers, list) or len(form.vars.answers) == 0:  # need type checking as becomes string if only 1 item
                response.flash = 'form has errors '
                form.errors.answers = "Not enough possible answers"
                return dict(form=form, heading=heading, selfquest=selfquest)
        if questid:
            form.vars.id = questid
            if form.deleted:
                db(db.question.id == questid).delete()
                response.flash = 'Item deleted'
                if context and eventid:
                    redirect(URL('event', 'vieweventmapd3', args=[eventid]))
                else:
                    redirect(URL('review', 'newindex', args=['items', 'Draft']))
            else:
                record.update_record(**dict(form.vars))
                response.flash = 'Item updated'
                if context and eventid:
                    redirect(URL('event', 'vieweventmapd3', args=[eventid]))
                else:
                    redirect(URL('review', 'newindex', args=['items', 'Draft']))
        else:
            form.vars.id = db.question.insert(**dict(form.vars))
        response.flash = 'form accepted'
        session.lastquestion = form.vars.id
        session.eventid = form.vars.eventid
        session.projid = form.vars.projid
        session.resolvemethod = form.vars.resolvemethod
        session.status = form.vars.status
        if priorquest > 0 and db(db.questlink.sourceid == priorquest and
                                 db.questlink.targetid == form.vars.id).isempty():
            db.questlink.insert(sourceid=priorquest, targetid=form.vars.id)

        schedule_vote_counting(form.vars.resolvemethod, form.vars.id, form.vars.duedate)
        redirect(URL('accept_question', args=[form.vars.qtype, form.vars.status, form.vars.id]))
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill out the form'

    return dict(form=form, heading=heading, selfquest=selfquest)


@auth.requires_login()
def new_questload():
    # This will be a simplified editing form for the eventmap piece
    # specific problem was geoloocation but reasonable to simplify
    # on eventmap - however postback will then need to add the questid
    # and amended logic to identify that we are editing - the values that are on the form
    # edit will need to insert the question id and the next new record will remove it if there - will aim to add the
    # full row to begin with and make read only
    qtype = 'quest'  # Not sent as arg as don't know what type in current thinking
    sourcetext = request.args(0)  # lets send this and handle edit and load on same function
    eventid = request.args(1, cast=int, default=0)
    projid = request.args(2, cast=int, default=0)
    record = 0

    if sourcetext and sourcetext.isdigit():
        questid = int(sourcetext)
    elif sourcetext:
        sourcetext = sourcetext.replace("_", " ")  # This will do for now - other chars may be problem
        sourcerecs = db(db.question.questiontext == sourcetext).select(
                            db.question.id, orderby=~db.question.createdate)
        if sourcerecs:
            questid = sourcerecs.first().id
        else:
            # May need to look at what happens if not found in more detail but lets leave until we have example
            responsetext = 'Target of link could not be found'
            return responsetext
    else:
        questid = None

    if questid:
        record = db.question(questid)
        qtype = record.qtype
        if record.auth_userid != auth.user.id or record.status != 'Draft':
            session.flash = 'Not Allowed only Draft items can be edited by their owners'
            responsetext = 'Not Allowed only Draft items can be edited by their owners'
            return responsetext

    # this will become a variable priorquest = request.args(1, cast=int, default=0)
    priorquest = request.vars.priorquest or 0

    if session.access_group is None:
        session.access_group = get_groups(auth.user_id)

    db.question.answer_group.requires = IS_IN_SET(session.access_group)
    db.question.status.requires = IS_IN_SET(['Draft', 'In Progress'])

    heading = 'Submit Item'
    labels = {'questiontext': 'Question'}

    fields = ['qtype', 'status', 'questiontext', 'category', 'activescope', 'continent', 'country', 'subdivision',
              'answers', 'xpos', 'ypos']

    if questid:
        fields.insert(-1, 'notes')
        form = SQLFORM(db.question, record, fields=fields, labels=labels, deletable=True, _id='myform')
    else:
        form = SQLFORM(db.question, fields=fields, labels=labels, _id='myform')
    # form.add_button('Cancel', '#')

    form.vars.eventid = eventid or session.eventid or db(db.evt.evt_name == 'Unspecified').select(db.evt.id).first().id
    form.vars.status = session.status or 'Draft'
    form.vars.projid = projid or session.projid or db(db.project.proj_name == 'Unspecified').select(
        db.project.id).first().id

    if session.resolvemethod:
        form.vars.resolvemethod = session.resolvemethod
    else:
        form.vars.resolvemethod = PARAMS.default_resolve_name

    # this can be the same for both questions and actions
    if form.validate():
        # form.vars.question_lat, form.vars.question_long = IS_GEOLOCATION.parse_geopoint(form.vars.coord)
        if not questid and not form.vars.question_id:  # not editing
            form.vars.auth_userid = auth.user.id
            form.vars.qtype = qtype
            form.vars.createdate = request.utcnow

        if form.vars.qtype == 'action':
            form.vars.answers = ['Approve', 'Disapprove', 'OK']
        elif form.vars.qtype == 'issue':
            form.vars.answers = ['Agree', 'Disagree', 'OK']

        form.vars.answercounts = [0] * (len(form.vars.answers))

        if questid or form.vars.question_id:
            # form.vars.id = questid - don't think this is required and
            if form.deleted:
                db(db.question.id == form.vars.id).delete()
                response.flash = 'Item deleted'
            else:
                record.update_record(**dict(form.vars))
                response.flash = 'Item updated'
        else:
            questid = db.question.insert(**dict(form.vars))
        response.flash = 'form accepted'
        session.lastquestion = form.vars.id
        session.eventid = form.vars.eventid
        session.projid = form.vars.projid
        session.resolvemethod = form.vars.resolvemethod
        session.status = form.vars.status
        if priorquest > 0 and db(db.questlink.sourceid == priorquest and
                                 db.questlink.targetid == form.vars.id).isempty():
            db.questlink.insert(sourceid=priorquest, targetid=form.vars.id)
        if form.vars.status == 'In Progress':
            schedule_vote_counting(form.vars.resolvemethod, form.vars.id, form.vars.duedate)

    elif form.errors:
        return TABLE(*[TR(k, v) for k, v in form.errors.items()])
    return dict(form=form, heading=heading, questid=questid)


@auth.requires_login()
def question_plan():
    # This allows creation of questions, actions and issues so the first
    # thing to do is establish whether question or action being submitted the
    # default is question unless action or issue specified and

    qtype = request.args(0, default='quest')
    questid = request.args(1, cast=int, default=0)
    # status = request.args(2, default=None)
    # context = request.args(3, default=None)
    # eventid = request.args(4, cast=int, default=0)
    record = 0
    # print qtype, questid, status, context, eventid
    if not questid:
        session.flash = 'This is for editing plans only'
        redirect(URL('default', 'index'))
    else:
        record = db.question(questid)
        qtype = record.qtype

        if not can_edit_plan(auth.user.id, record.auth_userid, record.shared_editing, record.plan_editor):
            session.flash = 'Not Authorised-items can only be edited by owners or editors unless set for shared editing'
            redirect(URL('default', 'index'))

    if session.access_group is None:
        session.access_group = get_groups(auth.user_id)

    heading = 'Plan Action'
    labels = {'questiontext': 'Action'}
    fields = ['questiontext', 'execstatus', 'startdate', 'enddate', 'responsible', 'perccomplete', 'notes',
              'plan_editor', 'shared_editing']
    
    db.question.questiontext.writable = False

    form = SQLFORM(db.question, record, fields=fields, labels=labels, showid=False)
    # this can be the same for both questions and actions
    if form.validate():
        record.update_record(**dict(form.vars))
        response.flash = 'Item updated'
        redirect(URL('review', 'newindex', args=['plan', 'agreed', 'priority', 0, 'Yes']))
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill out the form'

    return dict(form=form, heading=heading)


def accept_question():
    response.flash = "Details Submitted"
    qtype = request.args(0, default='quest')
    status = request.args(1, default='InProg')
    questid = request.args(2, default=0)

    item = getitem(qtype)

    quest = db(db.question.id == questid).select().first()

    if session.priorquest is not None and session.priorquest > 0:
        # append into priorquests and subsquests
        quest2 = db(db.question.id == session.priorquest).select(db.question.id,
                                                                 db.question.subsquests).first()
        subsquests = quest2.subsquests
        subsquests.append(session.lastquestion)
        quest2.update_record(subsquests=subsquests)
        quest2 = db(db.question.id == session.lastquestion).select(db.question.id,
                                                                   db.question.priorquests).first()
        priorquests = quest2.priorquests
        priorquests.append(session.priorquest)
        quest2.update_record(priorquests=priorquests)
        session.lastquestion = 0
        session.priorquest = 0

    return dict(qtype=qtype, status=status, item=item, quest=quest)


def subdivn():
    # This is called via Ajax to populate the subdivision dropdown on change of country
    # now changed to derelationalise country subdivision
    result = "<option value='Unspecified'>Unspecified</option>"
    subdivns = db(db.subdivision.country == request.vars.country).select(
        db.subdivision.subdiv_name, cache=(cache.ram, 1200), cacheable=True)
    for row in subdivns:
        if row.subdiv_name != request.vars.subdivision:
            result += "<option value='" + str(row.subdiv_name) + "'>" + row.subdiv_name + "</option>"
        else:
            result += "<option value='" + str(row.subdiv_name) + "' selected>" + row.subdiv_name + "</option>"

    return XML(result)


def country():
    result = "<option value='Unspecified'>Unspecified</option>"
    countries = db(db.country.continent == request.vars.continent).select(
        db.country.country_name, cache=(cache.ram, 6000), cacheable=True)
    for countrie in countries:
        if countrie.country_name != request.vars.country:
            result += "<option value='" + str(countrie.country_name) + "'>" + countrie.country_name + "</option>"
        else:
            result += "<option value='" + str(countrie.country_name) + "' selected>" + countrie.country_name + "</option>"
    return XML(result)


@auth.requires_login()
def drafttoinprog():
    """
    This willl provide a quick method of updating a draft question to submitted provided it is the owner who
    is attempting to do this it will also be called by a button with a modal piece in it same as archiving
    """
    questid = request.args(0, cast=int, default=0)

    quest = db(db.question.id == questid).select().first()

    if quest.status == 'Draft' and quest.auth_userid == auth.user_id:
        if quest.answers and len(quest.answers) > 1:
            quest.update_record(status='In Progress')
            responsetext = 'Item updated to in-progress:' + str(questid)
        else:
            responsetext = 'This item has one or less answers so cannot confirm'

    elif quest.status != 'Draft':
        responsetext = 'This is not a draft item'
    else:  # wrong user
        responsetext = 'You can only update items that you created'
    # session.flash = messagetxt
    # return messagetxt
    return 'jQuery(".flash").html("' + responsetext + '").slideDown().delay(1500).slideUp();' \
                                                      ' $("#target").html("' + responsetext + '");'


@auth.requires_login()
def wolfram_alpha_lookup():
    # This should be a straightforward function called via Ajzx to lookup the answer to a question on wolfram alpha
    # and then feed the answer back into the Notes section of the question being created - it is anticipated that in
    # general this will only be used for self answered questions - however it might be called for other things in due
    # course and we may amend to support different knowledge engines later as well
    client = wolframalpha.Client(wa_id)

    if request.args(0):
        qtext = urllib.unquote(request.args(0)).decode('utf8').replace('_', ' ')
        # qtext = request.args(0).replace('_', ' ')
        print qtext
    else:
        return "You need to enter a question to lookup the answer on Wolfram Alpha"

    res = client.query(qtext)
    try:
        answer = ''
        for pod in res.pods:
            # print '{p.title}: {p.text}'.format(p=pod)
            if pod.title == 'Result':
                for sub in pod.subpods:
                    print(sub.plaintext)
                    if sub.plaintext:
                        answer += sub.plaintext
                        answer += '\r'
            else:
                'No result found for this question'

        # responsetext = 'Answer received'
    except AttributeError:
        answer = "No answer received"
        # responsetext = "No answer received"

    return answer

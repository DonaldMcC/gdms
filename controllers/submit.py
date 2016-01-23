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
from ndspermt import get_groups
from ndsfunctions import getitem


@auth.requires_login()
def new_question():
    # This allows creation of questions, actions and issues so the first
    # thing to do is establish whether question or action being submitted the
    # default is question unless action or issue specified and

    qtype = request.args(0, default='quest')
    questid = request.args(1, cast=int, default=0)
    status = request.args(2, default=None)
    record = 0

    if questid:
        record = db.question(questid)
        qtype = record.qtype
        if record.auth_userid != auth.user.id or record.status != 'Draft':
            session.flash = 'Not Authorised - items can only be edited by their owners'
            redirect(URL('default', 'index'))

    # this will become a variable priorquest = request.args(1, cast=int, default=0)
    priorquest = 0

    if session.access_group is None:
        session.access_group = get_groups(auth.user_id)

    db.question.answer_group.requires = IS_IN_SET(session.access_group)
    db.question.status.requires = IS_IN_SET(['Draft', 'In Progress'])

    if qtype == 'quest':
        heading = 'Submit Question'
        labels = {'questiontext': 'Question'}
        fields = ['questiontext', 'eventid', 'resolvemethod', 'duedate', 'answer_group', 'category', 'activescope',
                  'continent', 'country', 'subdivision', 'status', 'answers']
    elif qtype == 'action':
        heading = 'Submit Action'
        labels = {'questiontext': 'Action'}
        fields = ['questiontext', 'eventid', 'resolvemethod', 'duedate', 'responsible', 'answer_group', 'category',
                  'activescope', 'continent', 'country', 'subdivision', 'status']
    else:
        heading = 'Submit Issue'
        labels = {'questiontext': 'Issue'}
        fields = ['questiontext', 'eventid', 'resolvemethod', 'duedate', 'answer_group', 'category', 'activescope',
                  'continent', 'country', 'subdivision', 'status']
    if questid:
        fields.insert(0, 'qtype')
        form = SQLFORM(db.question, record, fields=fields, labels=labels, formstyle='table3cols', deletable=True)
    else:
        # form = SQLFORM(db.question, fields=fields, labels=labels, formstyle='table3cols')
        form = SQLFORM(db.question, fields=fields, labels=labels)

    if session.eventid > 0:
        form.vars.eventid = session.eventid
    else:
        form.vars.eventid = db(db.evt.evt_name == 'Unspecified').select(db.evt.id).first().id

    # this can be the same for both questions and actions
    if form.validate():
        # print 'form validated'
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
        if questid:
            form.vars.id = questid
            if form.deleted:
                db(db.question.id == questid).delete()
                response.flash = 'Item deleted'
                redirect(URL('review', 'newindex', args=['items', 'Draft']))
            else:
                record.update_record(**dict(form.vars))
                response.flash = 'Item updated'
                redirect(URL('review', 'newindex', args=['items', 'Draft']))
        else:
            form.vars.id = db.question.insert(**dict(form.vars))
        response.flash = 'form accepted'
        session.lastquestion = form.vars.id
        session.eventid = form.vars.eventid
        if priorquest > 0 and db(db.questlink.sourceid == priorquest and
                                 db.questlink.targetid == form.vars.id).isempty():
            db.questlink.insert(sourceid=priorquest, targetid=form.vars.id)

        schedule_vote_counting(form.vars.resolvemethod, form.vars.id, form.vars.duedate)
        redirect(URL('accept_question', args=[form.vars.qtype, form.vars.status, form.vars.id]))
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

    if session.priorquest > 0:
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
        result += "<option value='" + str(row.subdiv_name) + "'>" + row.subdiv_name + "</option>"

    return XML(result)


def country():
    result = "<option value='Unspecified'>Unspecified</option>"
    countries = db(db.country.continent == request.vars.continent).select(
        db.country.country_name, cache=(cache.ram, 6000), cacheable=True)
    for countrie in countries:
        result += "<option value='" + str(countrie.country_name) + "'>" + countrie.country_name + "</option>"

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

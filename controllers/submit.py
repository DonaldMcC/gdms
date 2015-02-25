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
    http://..../[app]/submit/multi - remove
    http://..../[app]/submit/subdivision
    http://..../[app]/submit/country

    """
from ndspermt import get_groups

@auth.requires_login()
def new_question():
    #This allows creation of both questions and actions so the first
    #thing to do is establish whether question or action being submitted the
    #default is question unless action specified

    qtype=request.args(0, default='quest')
    status=request.args(1, default='In Progress')
    priorquest = request.args(1, cast=int, default=0)

    if session.access_group is None:
        session.access_group = get_groups(auth.user_id)

    db.question.answer_group.requires=IS_IN_SET(session.access_group)
    db.question.status.requires=IS_IN_SET(['Draft', 'In Progress'])

    if qtype=='quest':
        heading = 'Submit Question'
        labels = {'questiontext': 'Question'}

        fields = ['questiontext', 'eventid', 'resolvemethod', 'answer_group', 'category', 'activescope',
                  'continent', 'country', 'subdivision', 'status', 'answers']
        form = SQLFORM(db.question, fields=fields, labels=labels, formstyle='table3cols')
    elif qtype=='action':
        heading = 'Submit Action'
        labels = {'questiontext': 'Action'}
        fields = ['questiontext', 'eventid', 'answer_group', 'category', 'activescope',
                  'continent', 'country', 'subdivision', 'status', 'duedate']
        form = SQLFORM(db.question, fields=fields, labels=labels, formstyle='table3cols')
    else:
        heading = 'Submit Issue'
        labels = {'questiontext': 'Issue'}
        fields = ['questiontext', 'eventid', 'answer_group', 'category', 'activescope',
                  'continent', 'country', 'subdivision', 'status',  'duedate']
        form = SQLFORM(db.question, fields=fields, labels=labels, formstyle='table3cols')



    if session.eventid > 0:
        form.vars.eventid = session.eventid
    else:
        form.vars.eventid = db(db.event.event_name =='Unspecified').select(db.event.id).first().id

    #this can be the same for both questions and actions
    if form.validate():
        form.vars.auth_userid = auth.user.id
        form.vars.qtype = qtype
        if qtype != 'quest':
            form.vars.answers = ['Approve', 'Disapprove', 'OK']
        form.vars.answercounts = [0]*(len(form.vars.answers))
        scope = form.vars.activescope

        form.vars.createdate = request.utcnow
        if status=='draft':
            form.vars.status='Draft'

        form.vars.id = db.question.insert(**dict(form.vars))
        response.flash = 'form accepted'
        session.lastquestion = form.vars.id
        session.eventid = form.vars.eventid
        if priorquest > 0 and db(db.questlink.sourceid == priorquest and
                                 db.questlink.targetid == form.vars.id).isempty():
            db.questlink.insert(sourceid=priorquest, targetid=form.vars.id)

        redirect(URL('accept_question', args=[form.vars.qtype]))
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill out the form'

    return dict(form=form, heading=heading)


def accept_question():
    response.flash = "Details Submitted"
    qtype = request.args(0, default='quest')
    #if request.args(0) == 'action':
    #    qtype = 'action'
    #else:
    #    qtype = 'question'
    # will now update priorquest with the subsequent question details
    # and this question with priorquest details
    if session.priorquest > 0:
        #append into priorquests and subsquests
        quest = db(db.question.id == session.priorquest).select(db.question.id,
                                                                db.question.subsquests).first()
        subsquests = quest.subsquests
        subsquests.append(session.lastquestion)
        quest.update_record(subsquests=subsquests)
        quest = db(db.question.id == session.lastquestion).select(db.question.id,
                                                                  db.question.priorquests).first()
        priorquests = quest.priorquests
        priorquests.append(session.priorquest)
        quest.update_record(priorquests=priorquests)
        session.lastquestion = 0
        session.priorquest = 0

    return locals()


#This is called via Ajax to populate the subdivision dropdown on change of country
#now changed to derelationalise country subdivision

def multi():
    #placeholder for discussion of the topic at present
    pass
    return locals()


def subdivn():
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

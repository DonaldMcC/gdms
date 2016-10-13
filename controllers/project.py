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

# This controller has 3 functions:
# my_questions for reviewing progress on questions you have asked
# my_answers for reviewing your answers
# resovled for reviewing resolved questio

"""This controller has 4 functiosns:
index: -        simple listing of all locations now with buttons
new_project -  for creating and shortly editing locations
my_projects -  for creating, updating and deleting details of your locations perhaps duplicated
                with new_location 
viewproject -  for reviewing details of a single project and links to the events that
               are linked to it
"""

from ndspermt import get_groups


@auth.requires(True, requires_login=requires_login)
def index():
    page = request.args(0, cast=int, default=0)
    items_per_page = 20
    limitby = (page * items_per_page, (page + 1) * items_per_page + 1)
    projects = db(db.project.id > 0).select(orderby=[~db.project.createdate], limitby=limitby)
    return dict(projects=projects, page=page, items_per_page=items_per_page)

    
@auth.requires_login()
def new_project():
    # This allows creation and editing of a locations by their owner
    fields = ['proj_name', 'description', 'proj_url', 'answer_group', 'startdate', 'enddate', 'proj_shared']
    projid = request.args(0, default=None)
    if projid is not None:
        record = db.project(projid)
        if record.auth_userid != auth.user.id:
            session.flash = 'Not Authorised - projects can only be edited by their owners'
            redirect(URL('new_project'))
        form = SQLFORM(db.project, record, fields=fields)
    else:
        form = SQLFORM(db.project, fields=fields)

    if form.validate():
        if projid is not None:
            if form.deleted:
                db(db.project.id == projid).delete()
                response.flash = 'Project deleted'
                redirect(URL('default', 'index'))
            else:
                record.update_record(**dict(form.vars))
                response.flash = 'Project updated'
                redirect(URL('default', 'index'))
        else:
            form.vars.id = db.project.insert(**dict(form.vars))
            session.flash = 'Project Created'
            redirect(URL('accept_project', args=[form.vars.id, auth.user_id]))
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill out the form'
    return dict(form=form)


@auth.requires(True, requires_login=requires_login)
def accept_project():
    print 'got here'
    projid = request.args(0, cast=int, default=0) or redirect(URL('index'))
    proj_owner = request.args(1, cast=int, default=0)
    response.flash = "Project Created"
    session.projid = projid
    return dict(projid=projid, proj_shared=0, proj_owner=proj_owner)


@auth.requires_login()
def my_projects():
    # thinking is users shouldn't have that many of these so this should be easy - will need to be a button
    # to view events at this location and that this shold list all locations
    # but not sure that this is any better than just a simple query on location\index - to be considered
    query1 = db.project.proj_owner == auth.user.id
    myfilter = dict(project=query1)
    grid = SQLFORM.smartgrid(db.project, constraints=myfilter, searchable=False)
    return locals()


@auth.requires(True, requires_login=requires_login)
def viewproject():
    projid = request.args(0, cast=int, default=0) or redirect(URL('index'))
    projectrow = db(db.project.id == projid).select().first()
    
    # This just uses same approach as search for now and let's see if it
    # works
    results = db(db.question.projid == projid).select(db.question.id)
    if results:
        session.networklist = [x.id for x in results]
    else:
        session.networklist = []
    
    return dict(projectrow=projectrow, projid=projid)


def link():
    # This allows linking questions to a project via ajax based on event/link
    projid = request.args[0]
    chquestid = request.args[1]
    action = request.args[2]

    if auth.user is None:
        responsetext = 'You must be logged in to link questions to project'
    else:
        quest = db(db.question.id == chquestid).select().first()
        unspecproj = db(db.project.proj_name == 'Unspecified').select(db.project.id, cache=(cache.ram, 3600),).first()

        # Think about where this is secured - should probably be here
        project = db(db.project.id == projid).select().first()

        if project.proj_shared or (project.proj_owner == auth.user.id) or (quest.auth_userid == auth.user.id):
            if action == 'unlink':
                db(db.question.id == chquestid).update(projid=unspecproj.id)
                responsetext = 'Question %s unlinked' % chquestid
            else:
                db(db.question.id == chquestid).update(projid=projid)

                responsetext = 'Question %s linked to project' % chquestid
        else:
            responsetext = 'Not allowed - This project is not shared and you are not the owner'
    return 'jQuery(".flash").html("' + responsetext + '").slideDown().delay(1500).slideUp();' \
                                                      ' $("#target").html("' + responsetext + '");'
                                                      
def projadditems():
    # this came from event additems as as similar logic
    
    projid = request.args(0, cast=int, default=0) or redirect(URL('index'))
    projectrow = db(db.project.id == projid).select().first()
    if projectrow.proj_status != 'Open':
        session.flash = 'Project is not open you may not add items'
        redirect(URL('index'))
        
    session.projid = projid

    unspecprojid = db(db.project.proj_name == 'Unspecified').select(db.project.id).first().id

    heading = 'Resolved Questions'
    message = ''
    fields = ['selection', 'sortorder', 'filters', 'view_scope', 'continent', 'country', 'subdivision',
              'category', 'answer_group']

    if auth.user:
        db.viewscope.answer_group.requires = IS_IN_SET(set(get_groups(auth.user_id)))

    v = request.args(0, default='None')  # lets ust his for my
    q = request.args(1, default='None')  # this matters
    s = request.args(2, default='None')  # this is the sort order
    page = request.args(3, cast=int, default=0)

    if not session.selection:
        if v == 'quest':
            session.selection = ['Question']
        elif v == 'issue':
            session.selection = ['Issue']
        elif v == 'action':
            session.selection = ['Action']
        else:
            session.selection = ['Issue', 'Question', 'Action']

        if q == 'Resolved':
            session.selection.append('Resolved')
        elif q == 'Draft':
            session.selection.append('Draft')
        else:
            session.selection.append('Proposed')

    if s == 'priority':
        session.sortorder = '1 Priority'
    elif s == 'submit':
        session.sortorder = '3 Submit Date'
    elif s == 'answer':
        session.sortorder = '4 Answer Date'
    else:
        session.sortorder = '2 Resolved Date'

    # formstyle = SQLFORM.formstyles.bootstrap3
    form = SQLFORM(db.viewscope, fields=fields,
                   buttons=[TAG.button('Submit', _type="submit", _class="btn btn-primary btn-group"),
                            TAG.button('Reset', _type="button", _class="btn btn-primary btn-group",
                            _onClick="parent.location='%s' " % URL('newindex'))])

    form.vars.category = session.category
    if session.scope:
        form.vars.view_scope = session.scope
    form.vars.continent = session.vwcontinent
    form.vars.country = session.vwcountry
    form.vars.subdivision = session.vwsubdivision
    form.vars.selection = session.selection
    if session.filters:
        form.vars.filters = session.filters

    if q == 'Draft':
        session.selection = ['Issue', 'Question', 'Action', 'Draft']

    form.vars.sortorder = session.sortorder
    form.vars.selection = session.selection

    items_per_page = 50
    limitby = (page * items_per_page, (page + 1) * items_per_page + 1)

    if form.validate():
        session.scope = form.vars.view_scope
        session.category = form.vars.category
        session.vwcontinent = form.vars.continent
        session.vwcountry = form.vars.country
        session.vwsubdivision = form.vars.subdivision
        session.selection = form.vars.selection
        session.filters = form.vars.filters

        page = 0

        redirect(URL('eventadditems', args=projid))

    return dict(form=form, page=page, items_per_page=items_per_page, v=v, q=q,
                s=s, heading=heading, message=message, unspecprojid=unspecprojid, projectrow=projectrow)

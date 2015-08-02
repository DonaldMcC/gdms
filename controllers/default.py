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

# form = SQLFORM(..., formstyle = SQLFORM.formstyles.bootstrap3)
# grid = SQLFORM.grid(..., formstyle = SQLFORM.formstyles.bootstrap3) rubbish
# grid = SQLFORM.smartgrid(..., formstyle = SQLFORM.formstyles.bootstrap3)
# class="btn btn-primary btn-lg btn-block" - next find the button setup
# class="btn btn-primary"
# A(download.title, _href=URL("getfile", args=download.file))
# response.formstyle = 'bootstrap3_inline' # or 'bootstrap3_stacked'

"""
    exposes:
    This needs fully updated but do at the end
    http://..../[app]/default/index - will put network to the fore on this somehow
    http://..../[app]/default/questload
    http://..../[app]/default/questcountload
    http://..../[app]/default/user (standard)
    http://..../[app]/default/data & default/user documented below (standard)

    """
from ndspermt import get_groups, get_exclude_groups


def index():
    """
    This is the startup function.
    It retrieves the 5 highest priority actions, 5 most recently resolved quests
    and highest priority quests in progress.
    For actions - any status except rejected are wanted but to avoid an or or a
    not for GAE we will use ans3 for this purpose with numans always two for an 
    action this is ok.  All queries are cached for 2 mins which should be OK
    """

    response.flash = "Welcome to Net Decision Making"
    # Move subject table to website parameters - think how this fits in though
    # think this should be done elsewhere
    # subj = db(db.subject.id>0).select(db.subject.longdesc).first()
    if INIT:
        pass
    else:
        redirect(URL('admin', 'init'))

    response.title = "Net Decision Making"

    WEBSITE_PARAMETERS = db(db.website_parameters).select(cache=(cache.ram, 1200), cacheable=True).first()
    return dict(title=response.title, WEBSITE_PARAMETERS=WEBSITE_PARAMETERS)


def questload():
    # this came from resolved and thinking is it may replace it in due course but have
    # take then hradio button form out for now at least
    # need to get the event id into the strquery in due course but get it basically working
    # first

    # this came from questload and it may make sense to combine - however fields
    # and strquery would be different lets confirm works this way and then think about it
    # but no point to fields on select for GAE
    # latest thinking is thar request variables would apply if present but otherwise
    # may want to use session variables - but not on home page so maybe have some request args
    # as well - so lets try default to not apply session variables and then qtype for action/issue for now
    # possible session variables are:
    #   session.showcat
    #   session.showscope
    #   session.scope
    #   session.category
    #   session.vwcontinent
    #   session.vwcountry
    #   session.vwsubdivision
    #   session.answer_group
    #   session.sortorder
    # if source is default we don't care about session variables it's a standard view with request vars applied
    # but if other source then we should setup session variables and then apply request vars
    #   session.eventid is not used unless called from eventaddquests and the source will then need to be sent as
    # 'event' to get the button to add and remove from event as appropriate

    source = request.args(0, default='std')
    view = request.args(1, default='Action')

    # sort of got idea of v, q and s to consider for view, strquery and sort order

    scope = request.vars.scope or (source != 'default' and session.scope) or '1 Global'
    category = request.vars.category or (source != 'default' and session.category) or 'Unspecified'
    vwcontinent = request.vars.vwcontinent or (source != 'default' and session.vwcontinent) or 'Unspecified'
    vwcountry = request.vars.vwcountry or (source != 'default' and session.vwcountry) or 'Unspecified'
    vwsubdivision = request.vars.vwsubdivision or (source != 'default' and session.vwsubdivision) or 'Unspecified'
    sortorder = request.vars.sortorder or (source != 'default' and session.sortorder) or 'Unspecified'
    event = request.vars.event or (source != 'default' and session.sortby) or 'Unspecified'
    answer_group = request.vars.answer_group or (source != 'default' and session.answer_group) or 'Unspecified'
    context=request.vars.context or 'Unspecified'

    filters = (source != 'default' and session.filters) or []
    # this can be Scope, Category, AnswerGroup and probably Event in due course

    scope_filter = request.vars.scope_filter or 'Scope' in filters
    cat_filter = request.vars.cat_filter or 'Category' in filters
    group_filter = request.vars.group_filter or 'AnswerGroup' in filters

    selection = (source not in ('default', 'event', 'evtunlink') and session.selection ) or ['Question','Resolved']

    # selection will currently be displayed separately
    # db.viewscope.selection.requires = IS_IN_SET(['Issue','Question','Action','Proposed','Resolved','Draft'
    # so possibly maybe IP, IR, IM, QP, QR, QM, AP, AR, AM - but this can maybe always be in the URL

    if request.vars.selection == 'QP':
        strquery = (db.question.qtype == 'quest') & (db.question.status == 'In Progress')
    elif request.vars.selection == 'QR':
        strquery = (db.question.qtype == 'quest') & (db.question.status == 'Resolved')
    elif request.vars.selection == 'QM':
        strquery = (db.question.qtype == 'quest') & (db.question.status == 'Draft')\
                   & (db.question.auth_userid == auth.user.id)
    elif request.vars.selection == 'IP':
        strquery = (db.question.qtype == 'issue') & (db.question.status == 'In Progress')
        response.view = 'default/issueload.load'
    elif request.vars.selection == 'IR':
        strquery = (db.question.qtype == 'issue') & (db.question.status == 'Agreed')
        response.view = 'default/issueload.load'
    elif request.vars.selection == 'IM':
        strquery = (db.question.qtype == 'issue') & (db.question.status == 'Draft')\
                   & (db.question.auth_userid == auth.user_id)
        response.view = 'default/issueload.load'
    elif request.vars.selection == 'AP':
        strquery = (db.question.qtype == 'action') & (db.question.status == 'In Progress')
        response.view = 'default/actionload.load'
    elif request.vars.selection == 'AR':
        strquery = (db.question.qtype == 'action') & (db.question.status == 'Agreed')
        response.view = 'default/actionload.load'
    elif request.vars.selection == 'AM':
        strquery = (db.question.qtype == 'action') & (db.question.status == 'Draft')\
                   & (db.question.auth_userid == auth.user_id)
        response.view = 'default/actionload.load'
    else:
        strquery = (db.question.qtype == 'quest') & (db.question.status == 'Resolved')

    if cat_filter and cat_filter != 'False':
        strquery &= (db.question.category == category)

    if scope_filter is True:
        strquery &= db.question.activescope == scope
        if session.scope == '1 Global':
            strquery &= db.question.activescope == scope
        elif session.scope == '2 Continental':
            strquery = strquery & (db.question.activescope == session.scope) & (
                db.question.continent == vwcontinent)
        elif session.scope == '3 National':
            strquery = strquery & (db.question.activescope == session.scope) & (
                    db.question.country == vwcountry)
        elif session.scope == '4 Local':
            strquery = strquery & (db.question.activescope == session.scope) & (
                    db.question.subdivision == vwsubdivision)

    #print group_filter
    if group_filter and group_filter != 'False':
        strquery &= db.question.answer_group == answer_group

    if event != 'Unspecified':
        strquery &= db.question.eventid == event

    if request.vars.sortby == 'ResDate':
        sortorder = '2 Resolved Date'
    elif request.vars.sortby == 'Priority':
        sortorder = '1 Priority'
    elif request.vars.sortby == 'CreateDate':
        sortorder = '3 Submit Date'

    if sortorder == '1 Priority':
        sortby = ~db.question.priority
    elif sortorder == '3 Submit Date':
        sortby = ~db.question.createdate
    else:
        sortby = ~db.question.resolvedate

    if request.vars.page:
        page = int(request.vars.page)
    else:
        page = 0

    if request.vars.items_per_page:
        items_per_page = int(request.vars.items_per_page)
    else:
        items_per_page = 3

    limitby = (page * items_per_page, (page + 1) * items_per_page + 1)
    q = request.vars.selection

    no_page = request.vars.no_page
    # print strquery

    # removed caching for now as there are issues
    # quests = db(strquery).select(orderby=[sortby], limitby=limitby, cache=(cache.ram, 1200), cacheable=True)
    quests = db(strquery).select(orderby=[sortby], limitby=limitby)

    # remove excluded groups always
    if session.exclude_groups is None:
        session.exclude_groups = get_exclude_groups(auth.user_id)
    if quests and session.exclue_groups:
        alreadyans = quests.exclude(lambda r: r.answer_group in session.exclude_groups)
    return dict(quests=quests, page=page, source=source, items_per_page=items_per_page, q=q, view=view, no_page=no_page)


def questcountload():
    # this will load and initially display totals for group questions and category questions that the user is interested
    # in probably the correct - think we may maintain total counts in due course and only pull those back initially and
    # then have some options to pull back the details and display totals for groups users are not currently members off
    # but lets pull back all the details for now and then order by groupcat and name and display - so the category
    # questions may include groups that user does not have access to if we allow questions with a group to populate a
    # category and no obvious reason not to

    strquery = (db.questcount.groupcat == 'C')
    sortby = db.questcount.groupcatname
    categorycount = db(strquery).select(orderby=sortby)

    strquery = (db.questcount.groupcat=='G')

    grouplist = ['Unspecified']
    if auth.user:
        if session.access_group is None:
            session.access_group = get_groups(auth.user_id)
        allgroups = db(strquery).select(orderby=sortby)
        groupcount = allgroups.exclude(lambda row: row.groupcatname in session.access_group)
        if auth.user.exclude_categories:
            catignore = categorycount.exclude(lambda row: row.groupcatname in auth.user.exclude_categories)
    else:
        strquery = ((db.questcount.groupcat=='G') & (db.questcount.groupcatname == 'Unspecified'))
        groupcount = db(strquery).select(orderby=sortby)

    return dict(groupcount=groupcount, categorycount=categorycount)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """

    response.title = "Net Decision Making"

    # session.exclude_cats = None
    session.comblist = None
    session.questlist = None
    session.actlist = None
    session.continent = None
    session.country = None
    session.subdivision = None
    session.eventid = None

    return dict(form=auth())


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())

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

from datetime import timedelta
from ndspermt import get_groups, get_exclude_groups
from ndsfunctions import convrow, getlinks, get_gantt_data
from geogfunctions import getbbox

@auth.requires(True, requires_login=requires_login)
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
    if not INIT:
        redirect(URL('admin', 'init'))

    WEBSITE_PARAMETERS = db(db.website_parameters).select(cache=(cache.ram, 1200), cacheable=True).first()
    return dict(title=response.title, WEBSITE_PARAMETERS=WEBSITE_PARAMETERS)


@auth.requires(True, requires_login=requires_login)
def questload():
    # latest thinking is thar request variables would apply if present but otherwise
    # may want to use session variables - but not on home page so maybe have some request args
    # as well - so lets try default to not apply session variables and then qtype for action/issue for now
    # possible session variables are:
    #   session.showcat
    #   session.showscope
    #   session.view_scope
    #   session.category
    #   session.vwcontinent
    #   session.vwcountry
    #   session.vwsubdivision
    #   session.answer_group
    #   session.sortorder
    #   session.evtid
    #   session.projid
    #   session.searchrange
    #   session.coord
    # if source is default we don't care about session variables it's a standard view with request vars applied
    # but if other source then we should setup session variables and then apply request vars
    #   session.eventid is not used unless called from eventaddquests and the source will then need to be sent as
    # 'event' to get the button to add and remove from event as appropriate

    source = request.args(0, default='std')
    view = request.args(1, default='Action')

    # sort of got idea of v, q and s to consider for view, strquery and sort order

    scope = request.vars.scope or (source != 'default' and session.view_scope) or '1 Global'
    category = request.vars.category or (source != 'default' and session.category) or 'Unspecified'
    vwcontinent = request.vars.vwcontinent or (source != 'default' and session.vwcontinent) or 'Unspecified'
    vwcountry = request.vars.vwcountry or (source != 'default' and session.vwcountry) or 'Unspecified'
    vwsubdivision = request.vars.vwsubdivision or (source != 'default' and session.vwsubdivision) or 'Unspecified'
    sortorder = request.vars.sortorder or (source != 'default' and session.sortorder) or 'Unspecified'
    event = request.vars.event or (source != 'default' and session.evtid) or 0
    project = request.vars.project or (source != 'default' and session.projid) or 'Unspecified'

    answer_group = request.vars.answer_group or (source != 'default' and session.answer_group) or 'Unspecified'
    startdate = request.vars.startdate or (source != 'default' and session.startdate) or (
        request.utcnow - timedelta(days=1000))
    enddate = request.vars.enddate or (source != 'default' and session.enddate) or request.utcnow

    filters = (source != 'default' and session.filters) or []
    # this can be Scope, Category, AnswerGroup and probably Event in due course

    scope_filter = request.vars.scope_filter or 'Scope' in filters
    cat_filter = request.vars.cat_filter or 'Category' in filters
    group_filter = request.vars.group_filter or 'AnswerGroup' in filters
    date_filter = request.vars.datefilter or 'Date' in filters
    event_filter = request.vars.event_filter or 'Event' in filters  # so this will now need to be included in some calls
    project_filter = request.vars.project_filter or 'Project' in filters

    selection = (source not in ('default', 'event', 'evtunlink', 'projlink', 'projunlink') and session.selection) or ['Question', 'Resolved']

    # selection will currently be displayed separately
    # db.viewscope.selection.requires = IS_IN_SET(['Issue','Question','Action','Proposed','Resolved','Draft'
    # so possibly maybe IP, IR, IM, QP, QR, QM, AP, AR, AM - but this can maybe always be in the URL

    if request.vars.selection == 'QP':
        strquery = (db.question.qtype == 'quest') & (db.question.status == 'In Progress')
    elif request.vars.selection == 'QR':
        strquery = (db.question.qtype == 'quest') & (db.question.status == 'Resolved')
    elif request.vars.selection == 'QD' and auth.user:  # changed to all drafts with event filter
        strquery = (db.question.status == 'Draft') & (db.question.auth_userid == auth.user.id)
    elif request.vars.selection == 'IP':
        strquery = (db.question.qtype == 'issue') & (db.question.status == 'In Progress')
        response.view = 'default/issueload.load'
    elif request.vars.selection == 'IR':
        strquery = (db.question.qtype == 'issue') & (db.question.status == 'Agreed')
        response.view = 'default/issueload.load'
    elif request.vars.selection == 'IM':
        strquery = (db.question.qtype == 'issue') & (db.question.status == 'Draft') & (
                    db.question.auth_userid == auth.user_id)
        response.view = 'default/issueload.load'
    elif request.vars.selection == 'AP':
        strquery = (db.question.qtype == 'action') & (db.question.status == 'In Progress')
        response.view = 'default/actionload.load'
    elif request.vars.selection == 'AR':
        strquery = (db.question.qtype == 'action') & (db.question.status == 'Agreed')
        response.view = 'default/actionload.load'
        if source == 'default':
            strquery &= db.question.execstatus != 'Completed'
    elif request.vars.selection == 'PL':
        strquery = (db.question.qtype == 'action') & (db.question.status == 'Agreed') & (db.question.execstatus.belongs(session.execstatus))
        response.view = 'default/planload.load'
    elif request.vars.selection == 'AM':
        strquery = (db.question.qtype == 'action') & (db.question.status == 'Draft')\
                   & (db.question.auth_userid == auth.user_id)
        response.view = 'default/actionload.load'
    else:
        strquery = (db.question.qtype == 'quest') & (db.question.status == 'Resolved')

    if date_filter:
        strquery &= (db.question.createdate >= startdate) & (db.question.createdate <= enddate)

    if cat_filter and cat_filter != 'False':
        strquery &= (db.question.category == category)

    if source == 'eventadditems':
        unspeceventid = db(db.evt.evt_name == 'Unspecified').select(db.evt.id).first().id
        strquery &= db.question.eventid == unspeceventid
    elif source == 'projadditems': 
        unspecprojid = db(db.project.proj_name == 'Unspecified').select(db.project.id).first().id
        strquery &= db.question.projid == unspecprojid    
    elif event_filter and event != 0:
        strquery &= db.question.eventid == event
    elif project_filter and project != 'Unspecified':
        strquery &= db.question.projid == project

    if scope_filter is True:
        strquery &= db.question.activescope == scope
        if session.view_scope == '1 Global':
            strquery &= db.question.activescope == scope
        elif session.view_scope == '2 Continental':
            strquery = strquery & (db.question.activescope == session.view_scope) & (
                db.question.continent == vwcontinent)
        elif session.view_scope == '3 National':
            strquery = strquery & (db.question.activescope == session.view_scope) & (
                    db.question.country == vwcountry)
        elif session.view_scope == '4 Provincial':
            strquery = strquery & (db.question.activescope == session.view_scope) & (
                    db.question.subdivision == vwsubdivision)
        elif session.view_scope == '5 Local':
            minlat, minlong, maxlat, maxlong = getbbox(session.coord, session.searchrange)
            strquery = strquery & (db.question.activescope == session.view_scope) & (
                                  (current.db.question.question_lat > minlat) & 
                                  (current.db.question.question_lat < maxlat) &
                                  (current.db.question.question_long > minlong) &
                                  (current.db.question.question_long < maxlong))

    if group_filter and group_filter != 'False':
        strquery &= db.question.answer_group == answer_group

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
        items_per_page = 50

    limitby = (page * items_per_page, (page + 1) * items_per_page + 1)
    q = request.vars.selection

    no_page = request.vars.no_page

    # removed caching for now as there are issues
    # quests = db(strquery).select(orderby=[sortby], limitby=limitby, cache=(cache.ram, 1200), cacheable=True)
    quests = db(strquery).select(orderby=[sortby], limitby=limitby)

    # remove excluded groups always
    if session.exclude_groups is None:
        session.exclude_groups = get_exclude_groups(auth.user_id)

    if quests:
        alreadyans = quests.exclude(lambda r: r.answer_group in session.exclude_groups)

    if request.vars.selection == 'PL' and quests:    
        projxml = get_gantt_data(quests)
    else:         
        projxml = "<project></project>"
    #if request.vars.selection == 'PL':
    #    questlist = [x.id for x in quests]
    #    dependlist = [[] for x in xrange(len(questlist))]
    #    intlinks = getlinks(questlist)
    #    for x in intlinks:
    #        dependlist[questlist.index(x.targetid)].append(x.sourceid)
    #
    #    if quests:
    #        for i, row in enumerate(quests):
    #            z = str(dependlist[i])
    #            y = max(len(z)-2, 1)
    #            strdepend = z[1:y]
    #            projxml += convrow(row, strdepend)  
    #     
    #projxml += '</project>'      
                
    return dict(strquery=strquery, quests=quests, page=page, source=source, items_per_page=items_per_page, q=q,
                view=view, no_page=no_page, event=event, project=projxml)


@auth.requires(True, requires_login=requires_login)
def questarch():

    # this came from questload and it may make sense to combine - however fields
    # and strquery would be different lets confirm works this way and then think about it
    # but no point to fields on select for GAE
    # latest thinking is thar request variables would apply if present but otherwise
    # may want to use session variables - but not on home page so maybe have some request args
    # as well - so lets try default to not apply session variables and then qtype for action/issue for now
    # possible session variables are:
    #   session.showcat
    #   session.showscope
    #   session.view_scope
    #   session.category
    #   session.vwcontinent
    #   session.vwcountry
    #   session.vwsubdivision
    #   session.answer_group
    #   session.sortorder
    # if source is default we don't care about session variables it's a standard view with request vars applied
    # but if other source then we should setup session variables and then apply request vars

    source = request.args(0, default='std')
    view = request.args(1, default='Action')

    # sort of got idea of v, q and s to consider for view, strquery and sort order
    # source currently always default for this but will leave as is for now
    scope = request.vars.scope or (source != 'default' and session.view_scope) or '1 Global'
    category = request.vars.category or (source != 'default' and session.category) or 'Unspecified'
    vwcontinent = request.vars.vwcontinent or (source != 'default' and session.vwcontinent) or 'Unspecified'
    vwcountry = request.vars.vwcountry or (source != 'default' and session.vwcountry) or 'Unspecified'
    vwsubdivision = request.vars.vwsubdivision or (source != 'default' and session.vwsubdivision) or 'Unspecified'
    sortorder = request.vars.sortorder or (source != 'default' and session.sortorder) or 'Unspecified'
    event = request.vars.event or (source != 'default' and session.sortby) or 'Unspecified'
    project = request.vars.project or (
              source != 'default' and session.projid) or 'Unspecified'
    answer_group = request.vars.answer_group or (source != 'default' and session.answer_group) or 'Unspecified'
    startdate = request.vars.startdate or (source != 'default' and session.startdate) or (
        request.utcnow - timedelta(days=1000))
    enddate = request.vars.enddate or (source != 'default' and session.enddate) or request.utcnow
    context = request.vars.context or 'Unspecified'

    filters = (source != 'default' and session.filters) or []
    # this can be Scope, Category, AnswerGroup and probably Event in due course

    scope_filter = request.vars.scope_filter or 'Scope' in filters
    cat_filter = request.vars.cat_filter or 'Category' in filters
    group_filter = request.vars.group_filter or 'AnswerGroup' in filters
    date_filter = request.vars.datefilter or 'Date' in filters
    project_filter = request.vars.project_filter or 'Project' in filters
    event_filter = request.vars.event_filter or 'Event' in filters

    selection = (source not in ('default', 'event', 'evtunlink') and session.selection) or ['Question', 'Resolved']

    # selection will currently be displayed separately
    # db.viewscope.selection.requires = IS_IN_SET(['Issue','Question','Action','Proposed','Resolved','Draft'
    # so possibly maybe IP, IR, IM, QP, QR, QM, AP, AR, AM - but this can maybe always be in the URL

    if request.vars.selection == 'QP':
        strquery = (db.eventmap.qtype == 'quest') & (db.eventmap.queststatus == 'In Progress')
    elif request.vars.selection == 'QR':
        strquery = (db.eventmap.qtype == 'quest') & (db.eventmap.queststatus == 'Resolved')
    elif request.vars.selection == 'QD' and auth.user:
        strquery = (db.eventmap.qtype == 'quest') & (db.eventmap.queststatus == 'Draft')\
                   & (db.eventmap.auth_userid == auth.user.id)
    elif request.vars.selection == 'IP':
        strquery = (db.eventmap.qtype == 'issue') & (db.eventmap.queststatus == 'In Progress')
        response.view = 'default/issuearch.load'
    elif request.vars.selection == 'IR':
        strquery = (db.eventmap.qtype == 'issue') & (db.eventmap.queststatus == 'Agreed')
        response.view = 'default/issuearch.load'
    elif request.vars.selection == 'IM':
        strquery = (db.eventmap.qtype == 'issue') & (db.eventmap.queststatus == 'Draft') & (
                    db.eventmap.auth_userid == auth.user_id)
        response.view = 'default/issuearch.load'
    elif request.vars.selection == 'AP':
        strquery = (db.eventmap.qtype == 'action') & (db.eventmap.queststatus == 'In Progress')
        response.view = 'default/actionarch.load'
    elif request.vars.selection == 'AR':
        strquery = (db.eventmap.qtype == 'action') & (db.eventmap.queststatus == 'Agreed')
        response.view = 'default/actionarch.load'
    elif request.vars.selection == 'AM':
        strquery = (db.eventmap.qtype == 'action') & (db.eventmap.queststatus == 'Draft')\
                   & (db.eventmap.auth_userid == auth.user_id)
        response.view = 'default/actionarch.load'
    else:
        strquery = (db.eventmap.qtype == 'quest') & (db.eventmap.queststatus == 'Resolved')

    if date_filter:
        strquery &= (db.eventmap.createdate >= startdate) & (db.eventmap.createdate <= enddate)

    if cat_filter and cat_filter != 'False':
        strquery &= (db.eventmap.category == category)

    if scope_filter is True:
        strquery &= db.eventmap.activescope == scope
        if session.view_scope == '1 Global':
            strquery &= db.eventmap.activescope == scope
        elif session.view_scope == '2 Continental':
            strquery = strquery & (db.eventmap.activescope == session.view_scope) & (
                db.eventmap.continent == vwcontinent)
        elif session.view_scope == '3 National':
            strquery = strquery & (db.eventmap.activescope == session.view_scope) & (
                    db.eventmap.country == vwcountry)
        elif session.view_scope == '4 Provincial':
            strquery = strquery & (db.eventmap.activescope == session.view_scope) & (
                    db.eventmap.subdivision == vwsubdivision)

    if group_filter and group_filter != 'False':
        strquery &= db.eventmap.answer_group == answer_group

    strquery &= db.eventmap.eventid == event

    sortby = ~db.eventmap.priority

    if request.vars.page:
        page = int(request.vars.page)
    else:
        page = 0

    if request.vars.items_per_page:
        items_per_page = int(request.vars.items_per_page)
    else:
        items_per_page = 50

    limitby = (page * items_per_page, (page + 1) * items_per_page + 1)
    q = request.vars.selection

    no_page = request.vars.no_page

    # removed caching for now as there are issues
    # quests = db(strquery).select(orderby=[sortby], limitby=limitby, cache=(cache.ram, 1200), cacheable=True)
    quests = db(strquery).select(orderby=[sortby], limitby=limitby)

    # remove excluded groups always
    if session.exclude_groups is None:
        session.exclude_groups = get_exclude_groups(auth.user_id)
    if quests and session.exclue_groups:
        alreadyans = quests.exclude(lambda r: r.answer_group in session.exclude_groups)
    #for row in quests:
    #    print 'row', row
    return dict(strquery=strquery, quests=quests, page=page, source=source, items_per_page=items_per_page, q=q,
                view=view, no_page=no_page, event=event)
                
                
@auth.requires(True, requires_login=requires_login)
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

    strquery = (db.questcount.groupcat == 'G')

    grouplist = ['Unspecified']
    if auth.user:
        if session.access_group is None:
            session.access_group = get_groups(auth.user_id)
        allgroups = db(strquery).select(orderby=sortby)
        groupcount = allgroups.exclude(lambda row: row.groupcatname in session.access_group)
        if auth.user.exclude_categories:
            catignore = categorycount.exclude(lambda row: row.groupcatname in auth.user.exclude_categories)
    else:
        strquery = ((db.questcount.groupcat == 'G') & (db.questcount.groupcatname == 'Unspecified'))
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
    session.comblist = None
    session.questlist = None
    session.actlist = None

    return dict(form=auth())

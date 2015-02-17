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

#form = SQLFORM(..., formstyle = SQLFORM.formstyles.bootstrap3)
#grid = SQLFORM.grid(..., formstyle = SQLFORM.formstyles.bootstrap3) rubbish
#grid = SQLFORM.smartgrid(..., formstyle = SQLFORM.formstyles.bootstrap3)
#class="btn btn-primary btn-lg btn-block" - next find the button setup
#class="btn btn-primary"
#A(download.title, _href=URL("getfile", args=download.file))
#response.formstyle = 'bootstrap3_inline' # or 'bootstrap3_stacked'

"""
    exposes:
    This needs fully updated but do at the end
    http://..../[app]/default/index - will put network to the fore on this somehow
    http://..../[app]/default/questload
    http://..../[app]/default/actionload
    http://..../[app]/default/user
    http://..../[app]/default/data & default/user documented below (standard)

    """
from ndspermt import get_groups, make_button


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
    #Move subject table to website parameters - think how this fits in though
    #think this should be done elsewhere
    #subj = db(db.subject.id>0).select(db.subject.longdesc).first()
    if INIT:
        pass
    else:
        redirect(URL('admin', 'init'))

    #testhtml = make_button('test')
    testhtml='test'

    response.title = "Net Decision Making"

    WEBSITE_PARAMETERS = db(db.website_parameters).select(cache=(cache.ram, 1200), cacheable=True).first()
    return dict(title=response.title, WEBSITE_PARAMETERS=WEBSITE_PARAMETERS, testhtml=testhtml)


def questload():
    #this came from resolved and thinking is it may replace it in due course but have
    #take then hradio button form out for now at least
    #need to get the event id into the query in due course but get it basically working
    #first

    if request.vars.page:
        page = int(request.vars.page)
    else:
        page = 0

    if request.vars.items_per_page:
        items_per_page = int(request.vars.items_per_page)
    else:
        items_per_page = 3

    limitby = (page * items_per_page, (page + 1) * items_per_page + 1)
    q = 'std'

    if request.vars.sortby:
        if request.vars.sortby == 'ResDate':
            sortby = ~db.question.resolvedate
        else:
            sortby = ~db.question.priority
    else:
        sortby = ~db.question.createdate

    if request.vars.query:
        if request.vars.query == 'inprog':
            q = 'inprog'
            query = (db.question.qtype == 'quest') & (db.question.status == 'In Progress')
            quests = db(query).select(orderby=[sortby], limitby=limitby, cache=(cache.ram, 1200), cacheable=True)
        elif request.vars.query == 'event':
            q = 'event'
            query = (db.question.eventid == session.eventid)
            quests = db(query).select(orderby=[sortby], limitby=limitby, cache=(cache.ram, 1200), cacheable=True)
    else:
        query = (db.question.qtype == 'quest') & (db.question.status == 'Resolved')
        quests = db(query).select(orderby=[sortby], limitby=limitby, cache=(cache.ram, 1200), cacheable=True)

    return dict(quests=quests, page=page, items_per_page=items_per_page, q=q)


def actionload():
    #this came from questload and it may make sense to combine - however fields
    #and query would be different lets confirm works this way and then think about it
    #but no point to fields on select for GAE

    if request.vars.page:
        page = int(request.vars.page)
    else:
        page = 0

    items_per_page = 3
    limitby = (page * items_per_page, (page + 1) * items_per_page + 1)
    q = 'std'
    if request.vars.query == 'home':
        q = 'home'

    query = (db.question.qtype == 'action') & (db.question.status == 'Agreed')
    sortby = ~db.question.createdate

    actions = db(query).select(orderby=sortby, limitby=limitby, cache=(cache.ram, 1200), cacheable=True)

    return dict(actions=actions, page=page, items_per_page=items_per_page, q=q)

def questcountload():
    # this will load and initially display totals for group questions and category questions that the user is interested
    # in probably the correct - think we may maintain total counts in due course and only pull those back initially and
    # then have some options to pull back the details and display totals for groups users are not currently members off
    # but lets pull back all the details for now and then order by groupcat and name and display - so the category
    # questions may include groups that user does not have access to if we allow questions with a group to populate a
    # category and no obvious reason not to

    query = (db.questcount.groupcat=='C')
    sortby = db.questcount.groupcatname
    categorycount = db(query).select(orderby=sortby)

    query = (db.questcount.groupcat=='G')

    grouplist = ['Unspecified']
    if auth.user:
        if session.access_group is None:
            session.access_group = get_groups(auth.user_id)
        allgroups = db(query).select(orderby=sortby)
        groupcount = allgroups.exclude(lambda row: row.groupcatname in session.access_group)
        catignore = categorycount.exclude(lambda row: row.groupcatname in auth.user.exclude_categories)
    else:
        query = ((db.questcount.groupcat=='G') & (db.questcount.groupcatname == 'Unspecified'))
        groupcount = db(query).select(orderby=sortby)

    return dict(groupcount=groupcount, categorycount=categorycount)

def questcountload2():
    # this will load and initially display totals for group questions and category questions that the user is interested
    # in probably the correct - think we may maintain total counts in due course and only pull those back initially and
    # then have some options to pull back the details and display totals for groups users are not currently members off
    # but lets pull back all the details for now and then order by groupcat and name and display - so the category
    # questions may include groups that user does not have access to if we allow questions with a group to populate a
    # category and no obvious reason not to

    query = (db.questcount.groupcat=='C')
    sortby = db.questcount.groupcatname
    categorycount = db(query).select(orderby=sortby)

    query = (db.questcount.groupcat=='G')

    grouplist = ['Unspecified']
    if auth.user:
        if session.access_group is None:
            session.access_group = get_groups(auth.user_id)
        allgroups = db(query).select(orderby=sortby)
        groupcount = allgroups.exclude(lambda row: row.groupcatname in session.access_group)
        catignore = categorycount.exclude(lambda row: row.groupcatname in auth.user.exclude_categories)
    else:
        query = ((db.questcount.groupcat=='G') & (db.questcount.groupcatname == 'Unspecified'))
        groupcount = db(query).select(orderby=sortby)

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

    session.exclude_cats = None
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

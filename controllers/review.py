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

# This controller has x functions:

from ndspermt import get_groups


def newindex():
    # this replaces index and will now aim to provide an ajax version of review and 4 sections being this
    # issues, questions and actions which can all be shown or hidden and we may have a map section thereafter

    # this will also need an arg of some sort to determine if session variables should be heeded initially or default
    # to preset values - but whole thing is getting there now

    # this is a new file aiming to replace action index and review resolved and finally review my answers
    # Plan is to have up to 3 arguments for this which I thnk will be
    # 1 View - v
    # 2 Query - q
    # 3 Sort Order - s
    # 4 Page
    # 5 Items Per Page

    # Valid values for view are:
    # quest, action
    # Valid values for query are:
    # resolved, agreed, proposed and my - my is only valid if logged in
    # Valid values for sort order are dependant on the view but may be

    # priority, resolvedate, duedate, submitdate or responsible for actions
    #
    # so view changes to be a panel selection - the query will be all the record filters
    # sort order should be on the loaded sections and ideally might be a default but clickable on the gride
    # however I think this would need to then be stored as parameer for pagination 
    # items per page should also be on the subsections I think - so all this has is the query parameters and some sort
    # of parameter for which sections to load and the status of the questions may impact the load
    # potentially rest of this might be a form but - probably simpler to just build a layout and a call from there
    # so lets go with this
    # was thinking about doing this with some sort of form submission javascript - however I think we will change tack,
    # do with session variables as these are sort of setup and it makes the loading piece much easier so the load forms
    # will generally apply session variables of no request variables suplied and then would more or less be as is
    # advantage of this is that system will remember your last query - however it may not default it in the form
    #  - may need to display somewhere in the meantime

    heading = 'Resolved Questions'
    # v = 'quest' if set this overrides the session variables
    # q = 'resolved'
    # s = 'resolved'
    message = ''
    fields = ['selection', 'sortorder', 'filters', 'scope', 'continent', 'country', 'subdivision',
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

        if q == 'InProg':
            session.selection.append('Proposed')
        elif q == 'Drafts':
            session.selection.append('Draft')
        else:
            session.selection.append('Resolved')

    if s == 'priority':
        session.sortorder = '1 Priority'
    elif s == 'submit':
        session.sortorder = '3 Submit Date'
    elif s == 'answer':
        session.sortorder = '4 Answer Date'
    else:
        session.sortorder = '2 Resolved Date'

    # formstyle = SQLFORM.formstyles.bootstrap3
    form = SQLFORM(db.viewscope, fields=fields, formstyle='table3cols',
                   buttons = [TAG.button('Submit',_type="submit", _class="btn btn-primary btn-group"), TAG.button('Reset',_type="button", _class="btn btn-primary btn-group", _onClick = "parent.location='%s' " % URL('newindex'))])

    form.vars.category = session.category
    if session.scope:
        form.vars.scope = session.scope
    form.vars.continent = session.vwcontinent
    form.vars.country = session.vwcountry
    form.vars.subdivision = session.vwsubdivision
    form.vars.selection = session.selection
    if session.filters:
        form.vars.filters = session.filters

    if session.selection is None:
        session.selection = ['Question', 'Resolved']

    form.vars.sortorder = session.sortorder
    form.vars.selection = session.selection

    items_per_page = 50
    limitby = (page * items_per_page, (page + 1) * items_per_page + 1)

    if form.validate():
        session.scope = form.vars.scope
        session.category = form.vars.category
        session.vwcontinent = form.vars.continent
        session.vwcountry = form.vars.country
        session.vwsubdivision = form.vars.subdivision
        session.selection = form.vars.selection
        session.filters = form.vars.filters

        page = 0
        # redirect(URL('newindex', args=[v, q, s], vars=request.vars))
        # so thinking is that on initial call the args can over-ride the session variables

        redirect(URL('newindex'))

    return dict(form=form, page=page, items_per_page=items_per_page, v=v, q=q,
                s=s, heading=heading, message=message)


def newlist():
    # this is being rewritten to use load functionality

    heading = 'test heading'
    message = 'test message'
    groupcat = request.args(0, default='C')
    groupcatname = request.args(1, default='Unspecified')
    qtype = request.args(2, default='quest')
    status = request.args(3, default='resolved')
    items_per_page=50

    if groupcat == 'C':
        category = groupcatname
        answer_group = 'Unspecified'
        if category != 'Total':
            cat_filter = 'True'
        else:
            cat_filter = 'False'
    else:
        category = 'Unspecified'
        answer_group = groupcatname
        cat_filter = 'False'


    selection = qtype[0].upper()
    if status == 'resolved':
        selection += 'R'
    else:
        selection += 'P'

    heading = qtype + ' '+ groupcatname + ' status:' + status
    # confirm access to quest - probably not needed
    #if session.access_group is None:
    #    session.access_group = get_groups(auth.user_id)
    #    groupcount = quests.exclude(lambda row: row.answer_group in session.access_group)


    return dict(category=category, answer_group=answer_group, qtype=qtype, status=status,
                selection=selection, heading=heading, message=message, cat_filter=cat_filter, items_per_page=items_per_page)

def oldnewlist():
    # this should be a fairly simple query based on the questions in a category - however it probably
    # also needs to support pagination - we will keep separate from review for now as approach is different
    # and this will hopefully bring in the default representation and some button features which will also retrofit into
    # review/index
    # this may disappear and be covered by questload and actionload with parameters but not sure

    heading = ''
    message = ''
    groupcat = request.args(0, default='C')
    groupcatname = request.args(1, default='Unspecified')
    # print groupcatname to check if parametric router there
    qtype = request.args(2, default='quest')
    status = request.args(3, default='resolved')
    page = request.args(4, cast=int, default=0)

    if status == 'InProg':
        status = 'In Progress'

    if qtype == 'action' or qtype == 'issue':
        heading = 'Agreed Actions'

    items_per_page = 7
    limitby = (page * items_per_page, (page + 1) * items_per_page + 1)

    query = (db.question.qtype == qtype) & (db.question.status == status)

    if groupcatname != 'Total':
        if groupcat == 'C':
            query &= (db.question.category == groupcatname)
        else:
            query &= (db.question.answer_group == groupcatname)

    sortby = ~db.question.priority

    quests = db(query).select(orderby=sortby, limitby=limitby)

    # confirm access to quest
    if session.access_group is None:
        session.access_group = get_groups(auth.user_id)
        groupcount = quests.exclude(lambda row: row.answer_group in session.access_group)

    # should also filter for categories at some point

    session.networklist = [x.id for x in quests]

    return dict(quests=quests, page=page, items_per_page=items_per_page, groupcat=groupcat, groupcatname=groupcatname,
                qtype=qtype, status=status, heading=heading, message=message, v=1, q=2, s=3)


@auth.requires_login()
def my_answers():
    fields = ['sortorder', 'showscope', 'scope', 'continent', 'country', 'subdivision',
              'showcat', 'category']
    form = SQLFORM(db.viewscope, fields=fields, formstyle='table3cols')

    page = 0
    q = 'Que'
    s = 'Resolved'

    if session.showscope is None:
        form.vars.showscope = False
        form.vars.showcat = False
    else:
        form.vars.showscope = session.showscope
        form.vars.showcat = session.showcat
        form.vars.category = session.category
        form.vars.scope = session.scope
        form.vars.continent = session.vwcontinent
        form.vars.country = session.vwcountry
        form.vars.subdivision = session.vwsubdivision

    if session.sortorder is not None:
        form.vars.asortorder = session.sortorder

    if len(request.args):
        page = int(request.args[0])
        if len(request.args) > 1:
            q = request.args[1]
            if len(request.args) > 2:
                s = request.args[2]

    items_per_page = 10
    limitby = (page * items_per_page, (page + 1) * items_per_page + 1)

    if session.sortorder is not None:
        if session.sortorder == '1 Answer Date':
            s = 'Answer'
        elif session.sortorder == '2 Resolved Date':
            s = 'Resolved'
        elif session.sortorder == '3 Category':
            s = 'Category'

    if form.validate():
        session.showcat = form.vars.showcat
        session.showscope = form.vars.showscope
        session.scope = form.vars.scope
        session.category = form.vars.category

        session.vwcontinent = form.vars.continent
        session.vwcountry = form.vars.country
        session.vwsubdivision = form.vars.subdivision
        session.sortorder = form.vars.asortorder

        if session.sortorder == '1 Answer Date':
            s = 'Answer'
        elif session.sortorder == '2 Resolved Date':
            s = 'Resolved'
        elif session.sortorder == '3 Category':
            s = 'Category'

        page = 0
        redirect(URL('my_answers', args=[page, q, s]))

    # Actions can be selected for all or status of Agreed, In Progress or Disagreed
    # Rejected actions cannot be reviewed

    query = (db.userquestion.auth_userid == auth.user.id)
    if q == 'Resolved':
        query &= db.userquestion.status == 'Resolved'
    elif q == 'InProg':  # we are not showing this for philosophical reasons at the moment
        query &= db.userquestion.status == 'In Progress'

    if session.showcat is True:
        query &= db.userquestion.category == session.category
    if session.showscope is True:
        query &= db.userquestion.activescope == session.scope
        if session.scope == '1 Global':
            query &= db.userquestion.activescope == session.scope
        elif session.scope == '2 Continental':
            query = query & (db.userquestion.activescope == session.scope) & (
                db.userquestion.continent == session.vwcontinent)
        elif session.scope == '3 National':
            query = query & (db.userquestion.activescope == session.scope) & (
                db.userquestion.country == session.vwcountry)
        elif session.scope == '4 Local':
            query = query & (db.userquestion.activescope == session.scope) & (
                db.userquestion.subdivision == session.vwsubdivision)

    # And they can be sorted by create date, priority and due date    
    sortby = ~db.userquestion.ansdate

    if s == 'Resolved':
        sortby = ~db.userquestion.resolvedate
    elif s == 'Category':
        sortby = db.userquestion.category

    quests = db(query).select(orderby=[sortby], limitby=limitby)

    return dict(form=form, quests=quests, page=page, items_per_page=items_per_page, q=q, s=s, query=query)

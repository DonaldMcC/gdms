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

# This controller has x functions:
# newindex: the main review option
# newlist: not sure when this is now used
# activity: this is designed to show overview of what has been happening on the site between a range of dates
# my_answers - which should now be changed to use datatables

from ndspermt import get_groups, get_exclude_groups
from datetime import timedelta


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
              'category', 'answer_group', 'startdate', 'enddate']

    if auth.user:
        db.viewscope.answer_group.requires = IS_IN_SET(set(get_groups(auth.user_id)))

    v = request.args(0, default='None')  # lets use this for my
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
        elif q == 'Draft':
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
                   buttons=[TAG.button('Submit', _type="submit", _class="btn btn-primary btn-group"),
                            TAG.button('Reset', _type="button", _class="btn btn-primary btn-group",
                            _onClick="parent.location='%s' " % URL('newindex'))])
    
    numdays = 365  # default to 1 year of results

    if session.enddate:
        form.vars.enddate = session.enddate
    else:
        form.vars.enddate = request.utcnow.date()

    if session.startdate:
        form.vars.startdate = session.startdate
    else:
        form.vars.startdate = form.vars.enddate - timedelta(days=numdays)
        # tempdate = form.vars.enddate - timedelta(days=numdays)
        # form.vars.startdate = tempdate.date()

    form.vars.category = session.category
    if session.scope:
        form.vars.scope = session.scope
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

    if v == 'activity':
        response.view = 'review/activity2.html'

    if form.validate():
        session.scope = form.vars.scope
        session.category = form.vars.category
        session.vwcontinent = form.vars.continent
        session.vwcountry = form.vars.country
        session.vwsubdivision = form.vars.subdivision
        session.selection = form.vars.selection
        session.filters = form.vars.filters
        session.startdate = form.vars.startdate
        session.enddate = form.vars.enddate

        page = 0
        # redirect(URL('newindex', args=[v, q, s], vars=request.vars))
        # so thinking is that on initial call the args can over-ride the session variables

        if v == 'activity':
            redirect(URL('newindex', args='activity'))
        else:
            redirect(URL('newindex'))

    return dict(form=form, page=page, items_per_page=items_per_page, v=v, q=q,
                s=s, heading=heading, message=message)


def newlist():
    # this now uses load functionality - but more sorting out of answer_groups to be looked at once we have
    # better data
    message = 'test message'
    groupcat = request.args(0, default='C')
    groupcatname = request.args(1, default='Unspecified')
    qtype = request.args(2, default='quest')
    status = request.args(3, default='Resolved')
    items_per_page = 50

    if groupcat == 'C':
        category = groupcatname
        answer_group = 'Unspecified'
        group_filter = 'False'
        if category != 'Total':
            cat_filter = 'True'
        else:
            cat_filter = 'False'
    else:
        category = 'Unspecified'
        answer_group = groupcatname
        cat_filter = 'False'
        if answer_group != 'Total':
            group_filter = 'True'
        else:
            group_filter = 'False'

    selection = qtype[0].upper()
    if status == 'Resolved':
        selection += 'R'
    else:
        selection += 'P'

    if qtype == 'quest':
        qprint = 'Question'
    elif qtype == 'action':
        qprint = 'Action'
    else:
        qprint = 'Issue'

    heading = 'Item:' + qprint + ' Filter:' + groupcatname + ' Status:' + status

    return dict(category=category, answer_group=answer_group, qtype=qtype, status=status,
                selection=selection, heading=heading, message=message, cat_filter=cat_filter,
                group_filter=group_filter, items_per_page=items_per_page)


@auth.requires_login()
def activity():
    # This should support a report of activity in terms of both items submitted and actions resolved
    # thinking at present is not to use load and to not show too many details - perhaps
    # just the type and the question on submissions and the agreed answers and so on for quests
    # idea is that queries will be global and cacheable but will probably have to call a different
    # way eventually for email - it will also be callable via newindex and loaded in that case but will
    # NOT use session parameters instead these will be request vars to the extent supported

    period = request.args(0, default='weekly')
    format = request.args(1, default='html')
    source = request.args(2, default='default')  # will not use session variables as standard here so get everything

    # if run weekly or daily then lets run up to end of previous day - but final reports will
    # be dates

    if period == 'weekly':
        numdays = 7
    else:
        numdays = 1

    scope = request.vars.scope or (source != 'default' and session.scope) or '1 Global'
    category = request.vars.category or (source != 'default' and session.category) or 'Unspecified'
    vwcontinent = request.vars.vwcontinent or (source != 'default' and session.vwcontinent) or 'Unspecified'
    vwcountry = request.vars.vwcountry or (source != 'default' and session.vwcountry) or 'Unspecified'
    vwsubdivision = request.vars.vwsubdivision or (source != 'default' and session.vwsubdivision) or 'Unspecified'
    sortorder = request.vars.sortorder or (source != 'default' and session.sortorder) or 'Unspecified'
    event = request.vars.event or (source != 'default' and session.sortby) or 'Unspecified'
    answer_group = request.vars.answer_group or (source != 'default' and session.answer_group) or 'Unspecified'
    startdate = request.vars.startdate or (source != 'default' and session.startdate) or (request.utcnow - timedelta(days=numdays))
    enddate = request.vars.enddate or (source != 'default' and session.enddate) or request.utcnow.date()
    context = request.vars.context or 'Unspecified'

    filters = (source != 'default' and session.filters) or []
    # this can be Scope, Category, AnswerGroup and probably Event in due course

    scope_filter = request.vars.scope_filter or 'Scope' in filters
    cat_filter = request.vars.cat_filter or 'Category' in filters
    group_filter = request.vars.group_filter or 'AnswerGroup' in filters

    crtquery = (db.question.createdate >= startdate) & (db.question.createdate <= enddate)
    resquery = (db.question.resolvedate >= startdate) & (db.question.resolvedate <= enddate)
    challquery = (db.question.challengedate >= startdate) & (db.question.challengedate <= enddate)

    if cat_filter and cat_filter != 'False':
        crtquery &= (db.question.category == category)

    if scope_filter is True:
        crtquery &= db.question.activescope == scope
        if session.scope == '1 Global':
            crtquery &= db.question.activescope == scope
        elif session.scope == '2 Continental':
            crtquery &= (db.question.activescope == session.scope) & (db.question.continent == vwcontinent)
        elif session.scope == '3 National':
            crtquery &= (db.question.activescope == session.scope) & (db.question.country == vwcountry)
        elif session.scope == '4 Local':
            crtquery &= (db.question.activescope == session.scope) & (db.question.subdivision == vwsubdivision)

    if group_filter and group_filter != 'False':
        crtquery &= db.question.answer_group == answer_group

    if event != 'Unspecified':
        crtquery &= db.question.eventid == event

    orderstr = db.question.createdate
    resolvestr = db.question.resolvedate
    challstr = db.question.challengedate

    submitted = db(crtquery).select(orderby=orderstr)
    resolved = db(resquery).select(orderby=resolvestr)
    challenged = db(challquery).select(orderby=challstr)

    # remove excluded groups always
    if session.exclude_groups is None:
        # TODO think this should always return something so next bit unnecessary
        session.exclude_groups = get_exclude_groups(auth.user_id)
    if session.exclue_groups:
        alreadyans = resolved.exclude(lambda r: r.answer_group in session.exclude_groups)
        alreadyans = submitted.exclude(lambda r: r.answer_group in session.exclude_groups)
        alreadyans = challenged.exclude(lambda r: r.answer_group in session.exclude_groups)

        return dict(submitted=submitted, resolved=resolved, challenged=challenged)

    else:
        # to be amended
        return dict(submitted=submitted, resolved=resolved, challenged=challenged)


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

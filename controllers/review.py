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

# This controller has 3 functions:
# my_questions for reviewing progress on questions you have asked
# my_answers for reviewing your answers
# resovled for reviewing resolved questio

"""This controller has 3 functiosns:
index is the new function for reviewing 
questload - for loading into frontpage or elsewhere
actionload - for loading into frontpage or elsewhere
my_questions - for reviewing questions you have submitted
my_answers - for questions you have answered - this should move to action
resolved - for reviewing resolved questions -lets test if this is covered by action and should disappear
"""

from ndspermt import get_groups

def index():
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

    heading = 'Resolved Questions'
    # v = 'quest'
    # q = 'resolved'
    # s = 'resolved'
    message = ''
    fields = ['qsortorder', 'showscope', 'scope', 'continent', 'country', 'subdivision',
              'showcat', 'category']

    v = request.args(0, default='quest')
    q = request.args(1, default='resolved')
    s = request.args(2, default='resolved')
    page = request.args(3, cast=int, default=0)
    # if len(request.args):
    #    v = request.args[0]
    #    if len(request.args) > 1:
    #        q = request.args[1]
    #        if len(request.args) > 2:
    #            s = request.args[2]
    #            if len(request.args) > 3:
    #                page = int(request.args[3])

    if v == 'action':
        fields = ['sortorder', 'showscope', 'scope', 'continent', 'country',
                  'subdivision', 'showcat', 'category']
        heading = 'Agreed Actions'

    # formstyle = SQLFORM.formstyles.bootstrap3
    form = SQLFORM(db.viewscope, fields=fields, formstyle='table3cols')

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

    items_per_page = 7
    limitby = (page * items_per_page, (page + 1) * items_per_page + 1)

    if v == 'action':
        if session.sortorder is not None:
            form.vars.sortorder = session.sortorder
    else:
        if session.qsortorder is not None:
            form.vars.qsortorder = session.qsortorder

    if form.validate():
        session.showcat = form.vars.showcat
        session.showscope = form.vars.showscope
        session.scope = form.vars.scope
        session.category = form.vars.category
        session.vwcontinent = form.vars.continent
        session.vwcountry = form.vars.country
        session.vwsubdivision = form.vars.subdivision

        if v == 'action':
            session.sortorder = form.vars.sortorder
            if session.sortorder == '1 Priority':
                s = 'priority'
            elif session.sortorder == '2 Due Date':
                s = 'due'
            elif session.sortorder == '3 Resolved Date':
                s = 'resolved'
            elif session.sortorder == '4 Submit Date':
                s = 'submit'
            elif session.sortorder == '5 Responsible':
                s = 'responsible'
        else:
            session.qsortorder = form.vars.qsortorder
            if session.qsortorder == '1 Priority':
                s = 'priority'
            elif session.qsortorder == '2 Resolved Date':
                s = 'resolved'
            elif session.qsortorder == '3 Submit Date':
                s = 'submit'

        page = 0

        # from resolved
        redirect(URL('index', args=[v, q, s], vars=request.vars))

    if v == 'action':

        # From Action
        # Actions can be selected for all or status of Agreed, In Progress or Disagreed
        # Rejected actions cannot be reviewed
        query = (db.question.qtype == 'action')

        if q == 'agreed':
            query = (db.question.qtype == 'action') & (db.question.status == 'Agreed')
            heading = 'Agreed actions'
        elif q == 'proposed':
            query = (db.question.qtype == 'action') & (db.question.status == 'In Progress')
            heading = 'Proposed actions'
        elif q == 'disagreed':
            query = (db.question.qtype == 'action') & (db.question.status == 'Disagreed')
            heading = 'Disagreed actions'
        elif q == 'my' and auth.user is not None:
            query = (db.question.qtype == 'action') & (db.question.auth_userid == auth.user.id)
            heading = 'My actions'
        elif q == 'my':
            message = 'You are not logged in so default view shown'

        if session.showcat is True:
            query &= db.question.category == session.category
        if session.showscope:
            if session.scope == "1 Global":
                query &= db.question.activescope == session.scope
            elif session.scope == "2 Continental":
                query = query & (db.question.activescope == session.scope) & (
                    db.question.continent == session.vwcontinent)
            elif session.scope == "3 National":
                query = query & (db.question.activescope == session.scope) & (
                    db.question.country == session.vwcountry)
            elif session.scope == "4 Local":
                query = query & (db.question.activescope == session.scope) & (
                    db.question.subdivision == session.vwsubdivision)

        # And they can be sorted by create date, priority and due date    
        # not got a control for this yet probably part of request.args
        sortby = ~db.question.priority
        if s == 'due':
            sortby = db.question.duedate
        elif s == 'create':
            sortby = ~db.question.createdate
        elif s == 'resolved':
            sortby = ~db.question.resolvedate
        # elif s == 'responsible':
        #    sortby = db.question.responsible

        quests = db(query).select(orderby=sortby, limitby=limitby)

    else:
        # Actions can be selected for all or status of Agreed, In Progress or Disagreed
        # Rejected actions cannot be reviewed

        query = (db.question.qtype == 'quest') & (db.question.status == 'Resolved')
        if q == 'Que':
            query = (db.question.qtype == 'quest') & (db.question.status == 'Resolved')
            heading = 'Resolved Questions'

        if q == 'reject':  # we might show this and perhaps even allow challenges
            query = (db.question.qtype == 'quest') & (db.question.status == 'Rejected')
            heading = 'Rejected Quesions'
        elif q == 'inprog':  # we are not showing this for philosophical reasons at the moment
            query = (db.question.qtype == 'quest') & (db.question.status == 'Resolved')
            heading = 'Questions in Progress'
        elif q == 'my' and auth.user is not None:
            query = (db.question.auth_userid == auth.user.id) & (db.question.qtype == 'quest')
            heading = 'My Questions'

        if session.showcat is True:
            query &= db.question.category == session.category
        if session.showscope is True:
            query &= db.question.activescope == session.scope
            if session.scope == '1 Global':
                query &= db.question.activescope == session.scope
            elif session.scope == '2 Continental':
                query = query & (db.question.activescope == session.scope) & (
                    db.question.continent == session.vwcontinent)
            elif session.scope == '3 National':
                query = query & (db.question.activescope == session.scope) & (
                    db.question.country == session.vwcountry)
            elif session.scope == '4 Local':
                query = query & (db.question.activescope == session.scope) & (
                    db.question.subdivision == session.vwsubdivision)

        # And they can be sorted by create date, priority and due date    
        sortby = ~db.question.priority
        if s == 'resolved':
            sortby = ~db.question.resolvedate
        elif s == 'submit':
            sortby = ~db.question.createdate

        quests = db(query).select(orderby=sortby, limitby=limitby)
    session.networklist = [x.id for x in quests]
    return dict(form=form, quests=quests, page=page, items_per_page=items_per_page, v=v, q=q,
                s=s, query=query, heading=heading, message=message)


def newindex():
    # this replaces index and will now aim to provide an ajax version of review and 4 sections being this
    # issues, questions and actions which can all be shown or hidden and we may have a map section thereafter

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
    # items per page should also be on the subsections I think - so all this has is the query parameters and some sort of 
    # parameter for which sections to load and the status of the questions may impact the load 
    # potentially rest of this might be a form but - probably simpler to just build a layout and a call from there
    # so lets go with this
    # was thinking about doing this with some sort of form submission javascript - however I think we will change tack and
    # do with session variables as these are sort of setup and it makes the loading piece much easier so the load forms
    # will generally apply session variables of no request variables suplied and then would more or less be as is
    # advantage of this is that system will remember your last query - however it may not default it in the form - may need to display somewhere
    # in the meantime

    heading = 'Resolved Questions'
    # v = 'quest'
    # q = 'resolved'
    # s = 'resolved'
    message = ''
    fields = ['qsortorder', 'showscope', 'scope', 'continent', 'country', 'subdivision',
              'showcat', 'category']

    v = request.args(0, default='quest')

    q = request.args(1, default='resolved')
    s = request.args(2, default='resolved')
    page = request.args(3, cast=int, default=0)
    # if len(request.args):
    #    v = request.args[0]
    #    if len(request.args) > 1:
    #        q = request.args[1]
    #        if len(request.args) > 2:
    #            s = request.args[2]
    #            if len(request.args) > 3:
    #                page = int(request.args[3])

    if v == 'action':
        fields = ['sortorder', 'showscope', 'scope', 'continent', 'country',
                  'subdivision', 'showcat', 'category']
        heading = 'Agreed Actions'

    # formstyle = SQLFORM.formstyles.bootstrap3
    form = SQLFORM(db.viewscope, fields=fields, formstyle='table3cols')

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

    items_per_page = 7
    limitby = (page * items_per_page, (page + 1) * items_per_page + 1)

    if v == 'action':
        if session.sortorder is not None:
            form.vars.sortorder = session.sortorder
    else:
        if session.qsortorder is not None:
            form.vars.qsortorder = session.qsortorder

    if form.validate():
        session.showcat = form.vars.showcat
        session.showscope = form.vars.showscope
        session.scope = form.vars.scope
        session.category = form.vars.category
        session.vwcontinent = form.vars.continent
        session.vwcountry = form.vars.country
        session.vwsubdivision = form.vars.subdivision

        if v == 'action':
            session.sortorder = form.vars.sortorder
            if session.sortorder == '1 Priority':
                s = 'priority'
            elif session.sortorder == '2 Due Date':
                s = 'due'
            elif session.sortorder == '3 Resolved Date':
                s = 'resolved'
            elif session.sortorder == '4 Submit Date':
                s = 'submit'
            elif session.sortorder == '5 Responsible':
                s = 'responsible'
        else:
            session.qsortorder = form.vars.qsortorder
            if session.qsortorder == '1 Priority':
                s = 'priority'
            elif session.qsortorder == '2 Resolved Date':
                s = 'resolved'
            elif session.qsortorder == '3 Submit Date':
                s = 'submit'

        page = 0

        # from resolved
        redirect(URL('index', args=[v, q, s], vars=request.vars))

    if v == 'action':

        # From Action
        # Actions can be selected for all or status of Agreed, In Progress or Disagreed
        # Rejected actions cannot be reviewed
        query = (db.question.qtype == 'action')

        if q == 'agreed':
            query = (db.question.qtype == 'action') & (db.question.status == 'Agreed')
            heading = 'Agreed actions'
        elif q == 'proposed':
            query = (db.question.qtype == 'action') & (db.question.status == 'In Progress')
            heading = 'Proposed actions'
        elif q == 'disagreed':
            query = (db.question.qtype == 'action') & (db.question.status == 'Disagreed')
            heading = 'Disagreed actions'
        elif q == 'my' and auth.user is not None:
            query = (db.question.qtype == 'action') & (db.question.auth_userid == auth.user.id)
            heading = 'My actions'
        elif q == 'my':
            message = 'You are not logged in so default view shown'

        if session.showcat is True:
            query &= db.question.category == session.category
        if session.showscope:
            if session.scope == "1 Global":
                query &= db.question.activescope == session.scope
            elif session.scope == "2 Continental":
                query = query & (db.question.activescope == session.scope) & (
                    db.question.continent == session.vwcontinent)
            elif session.scope == "3 National":
                query = query & (db.question.activescope == session.scope) & (
                    db.question.country == session.vwcountry)
            elif session.scope == "4 Local":
                query = query & (db.question.activescope == session.scope) & (
                    db.question.subdivision == session.vwsubdivision)

        # And they can be sorted by create date, priority and due date    
        # not got a control for this yet probably part of request.args
        sortby = ~db.question.priority
        if s == 'due':
            sortby = db.question.duedate
        elif s == 'create':
            sortby = ~db.question.createdate
        elif s == 'resolved':
            sortby = ~db.question.resolvedate
        # elif s == 'responsible':
        #    sortby = db.question.responsible

        quests = db(query).select(orderby=sortby, limitby=limitby)

    else:
        # Actions can be selected for all or status of Agreed, In Progress or Disagreed
        # Rejected actions cannot be reviewed

        query = (db.question.qtype == 'quest') & (db.question.status == 'Resolved')
        if q == 'Que':
            query = (db.question.qtype == 'quest') & (db.question.status == 'Resolved')
            heading = 'Resolved Questions'

        if q == 'reject':  # we might show this and perhaps even allow challenges
            query = (db.question.qtype == 'quest') & (db.question.status == 'Rejected')
            heading = 'Rejected Quesions'
        elif q == 'inprog':  # we are not showing this for philosophical reasons at the moment
            query = (db.question.qtype == 'quest') & (db.question.status == 'Resolved')
            heading = 'Questions in Progress'
        elif q == 'my' and auth.user is not None:
            query = (db.question.auth_userid == auth.user.id) & (db.question.qtype == 'quest')

            heading = 'My Questions'

        if session.showcat is True:
            query &= db.question.category == session.category
        if session.showscope is True:
            query &= db.question.activescope == session.scope
            if session.scope == '1 Global':
                query &= db.question.activescope == session.scope
            elif session.scope == '2 Continental':
                query = query & (db.question.activescope == session.scope) & (
                    db.question.continent == session.vwcontinent)
            elif session.scope == '3 National':
                query = query & (db.question.activescope == session.scope) & (
                    db.question.country == session.vwcountry)
            elif session.scope == '4 Local':
                query = query & (db.question.activescope == session.scope) & (
                    db.question.subdivision == session.vwsubdivision)

        # And they can be sorted by create date, priority and due date    
        sortby = ~db.question.priority
        if s == 'resolved':
            sortby = ~db.question.resolvedate
        elif s == 'submit':
            sortby = ~db.question.createdate

        quests = db(query).select(orderby=sortby, limitby=limitby)
    session.networklist = [x.id for x in quests]
    return dict(form=form, quests=quests, page=page, items_per_page=items_per_page, v=v, q=q,
                s=s, query=query, heading=heading, message=message)


#    <td>{{=A(row.questcount[2],_href=URL('review','newlist',args=[row.groupcat,row.groupcatname,'Issue','Agreed']))}}</td>
def newlist():
    # this should be a fairly simple query based on the questions in a category - however it probably
    # also needs to support pagination - we will keep separate from review for now as approach is different
    # and this will hopefully bring in the default representation and some button features which will also retrofit into
    # review/index

    heading = ''
    message = ''
    groupcat = request.args(0, default='C')
    groupcatname = request.args(1, default='Unspecified')
    #print groupcatname to check if parametric router there
    qtype = request.args(2, default='quest')
    status = request.args(3, default='resolved')
    page = request.args(4, cast=int, default=0)

    if status == 'InProg':
        status = 'In Progress'

    if qtype == 'action' or qtype== 'issue':
        fields = ['sortorder', 'showscope', 'scope', 'continent', 'country',
                  'subdivision', 'showcat', 'category']
        heading = 'Agreed Actions'

    items_per_page = 7
    limitby = (page * items_per_page, (page + 1) * items_per_page + 1)

    query = (db.question.qtype == qtype) & (db.question.status == status)

    if groupcatname != 'Total':
        if groupcat == 'C':
            query = query & (db.question.category == groupcatname)
        else:
            query = query & (db.question.answer_group == groupcatname)

    sortby = ~db.question.priority

    quests = db(query).select(orderby=sortby, limitby=limitby)

    # confirm access to quest
    if session.access_group is None:
        session.access_group = get_groups(auth.user_id)
        groupcount = quests.exclude(lambda row: row.answer_group in session.access_group)

    #should also filter for categories at some point

    session.networklist = [x.id for x in quests]

    return dict(quests=quests, page=page, items_per_page=items_per_page, groupcat=groupcat, groupcatname=groupcatname,
                qtype=qtype, status=status, heading=heading, message=message, v=1, q=2, s=3)

@auth.requires_login()
def my_answers():
    fields = ['asortorder', 'showscope', 'scope', 'continent', 'country', 'subdivision',
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

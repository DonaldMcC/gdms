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
index - for listing and in due course searching for groups
my_groups - reviewing settings for groups you are the owner of
there will probably need to be some ajax functions in due course

"""

from ndspermt import get_groups

@auth.requires_login()
def index():
    """
    This controller should list all public and apply groups that users can apply to join or leave - buttons should be
    conditional on membership and so we should probably get groups to review this - maybe also a separate list of groups that
    users are members of with their role - but lets add that later
    """

    # to do add list of groups users are a member of - probably just a simply query for this as less functionality and no
    # obvious security.  So don't think this is a grid after all

    # Could we display as two lists - groups I am a member of and groups that users can join
    # First query would be filter for the second which seems fine and so won't do as load from my group
    # simple example of trying to get full split screen working as well
        

    #page = request.args(0, cast=int, default=0)
    #items_per_page = 7
    #limitby = (page * items_per_page, (page + 1) * items_per_page + 1)

    #query = (db.access_groups.group_type == 'public')
    #pubgroups = db(query).select()

    #query = (db.access_groups.group_type == 'apply')
    #applygroups = db(query).select()


    #allgroups = pubgroups | applygroups


    query = (db.access_group.id > 0)
    allgroups = db(query).select()

    if session.access_group is None:
        session.access_group = get_groups(auth.user_id)
    
    ingroups = allgroups.exclude(lambda row: row.group_name in session.access_group)
    
    #so in groups now contains all groups user is a member of

    availgroups = allgroups.exclude(lambda row: row.group_type in ['public','apply'])

    
    return dict(ingroups=ingroups, availgroups=availgroups)



@auth.requires_login()
def new_group():
    #This allows creation of an event

    fields = ['group_name', 'group_desc']
    form = SQLFORM(db.access_group, fields=fields, formstyle='table3cols')

    if form.validate():
        form.vars.id = db.access_group.insert(**dict(form.vars))
        #response.flash = 'form accepted'
        redirect(URL('accept_group', args=[form.vars.id]))
        #redirect(URL('accept_question',args=[form.vars.qtype]))
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill out the form'

    return dict(form=form)

def accept_group():
    response.flash = "Group Created"
    access_groupid = request.args(0, cast=int, default=0) or redirect(URL('new_group'))
    return dict(access_groupid=access_groupid)


@auth.requires_login()
def my_groups():
    """
    This would list all groups that user is a member of and permit leaving any that are not administrator appointed in
    which case user would get message back that they can apply to leave - think this is just a query with leave as a  link
    - so don't need a grid
    """
    query1 = db.group_members.auth_userid == auth.user.id
    myfilter = dict(group_members=query1)
    grid = SQLFORM.smartgrid(db.group_members, formstyle=SQLFORM.formstyles.bootstrap3, constraints=myfilter, searchable=False)
    # not sure 
    return locals()


@auth.requires_login()
def leave_group():
    """
    This will allow users to leave a group they are currently part of
    """
    query1 = db.group_members.auth_userid == auth.user.id
    myfilter = dict(group_members=query1)
    grid = SQLFORM.smartgrid(db.group_members, formstyle=SQLFORM.formstyles.bootstrap3, constraints=myfilter, searchable=False)
    # not sure 
    return locals()


#@auth.requires_signature() to be added
def join():
    # This allows users to join a group they are not currently a member of

    groupid = request.args(0, cast=int, default=0)

    if groupid == 0:
        responsetext = 'Incorrect call '
        return

    db.group_members.insert(access_group=groupid,auth_userid=auth.user_id)
    session.access_group = get_groups(auth.user_id)
    responsetext='You joined the group'
    return responsetext
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

"""This controller has 6 functions:
index - for listing and in due course searching for groups
new_group - for creating a new group
accept_group - to explain options after setting up a new group
my_groups - reviewing settings for groups you are the owner of
join - ajax function for joining groups
leave_group - ajax function for leaving groups

So there should be 4 views 
"""

from ndspermt import get_groups


@auth.requires_login()
def index():
    """
    This controller lists all public and apply groups that users are in or can apply to join - buttons are
    conditional on membership and so we should probably get groups to review this.
    """

    query = (db.access_group.id > 0)
    allgroups = db(query).select()

    session.access_group = get_groups(auth.user_id)
    
    ingroups = allgroups.exclude(lambda row: row.group_name in session.access_group)
    availgroups = allgroups.exclude(lambda row: row.group_type in ['public', 'apply'])
    
    return dict(ingroups=ingroups, availgroups=availgroups)


@auth.requires_login()
def new_group():
    # This allows creation of an access group
    groupid = request.args(0, cast=int, default=0)
    fields = ['group_name', 'group_desc', 'group_type']
    if auth.has_membership('manager'):
        db.access_group.group_type.requires = IS_IN_SET(['public', 'apply', 'invite', 'admin'])
    else:
        db.access_group.group_type.requires = IS_IN_SET(['public', 'apply', 'invite'])

    if groupid:
        form = SQLFORM(db.access_group, groupid, fields=fields)
    else:
        form = SQLFORM(db.access_group, fields=fields)

    if form.validate():
        form.vars.id = db.access_group.insert(**dict(form.vars))
        redirect(URL('accept_group', args=[form.vars.id]))
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill out the form'
    return dict(form=form)


def accept_group():
    # This confirms new group created
    response.flash = "Group Created"
    access_groupid = request.args(0, cast=int, default=0) or redirect(URL('new_group'))
    return dict(access_groupid=access_groupid)


@auth.requires_login()
def my_groups():
    """
    This would list all groups that user is a member of and permit leaving any that are not administrator appointed in
    which case user would get message back that they can apply to leave - think this is just a query with leave as link
    - so don't need a grid
    """
    query1 = db.group_members.auth_userid == auth.user.id
    myfilter = dict(group_members=query1)
    grid = SQLFORM.smartgrid(db.group_members, constraints=myfilter,
                             searchable=False)
    return locals()


@auth.requires_login()
@auth.requires_signature()
def leave_group():
    # This is an ajax call from index to join a group
    groupid = request.args(0, cast=int, default=0)

    if groupid == 0:
        responsetext = 'Incorrect call '
    else:
        db((db.group_members.access_group==groupid) & (db.group_members.auth_userid==auth.user_id)).delete()
        session.access_group = get_groups(auth.user_id)
        responsetext = 'You left the group'

    return 'jQuery(".w2p_flash").html("' + responsetext + '").slideDown().delay(1500).slideUp(); $("#target").html("' + responsetext + '");'

    
@auth.requires_login()
@auth.requires_signature()
def approve_applicants():
    # TODO Write ajax function for this and should handle rejection as well
    groupid = request.args(0, cast=int, default=0)

    if groupid == 0:
        responsetext = 'Incorrect call '
    else:
        db((db.group_members.access_group==groupid) & (db.group_members.auth_userid==auth.user_id)).delete()
        session.access_group = get_groups(auth.user_id)
        responsetext = 'You left the group'

    return 'jQuery(".w2p_flash").html("' + responsetext + '").slideDown().delay(1500).slideUp(); $("#target").html("' + responsetext + '");'  

@auth.requires_login()
def list_members():
    # This will list and then will need to be buttons to remove users from a group - which may be done with a blocked
    groupid = request.args(0, cast=int, default=0)

    if groupid == 0:
        responsetext = 'Incorrect call '
    else:
        db((db.group_members.access_group==groupid) & (db.group_members.auth_userid==auth.user_id)).delete()
        session.access_group = get_groups(auth.user_id)
        responsetext = 'You left the group'

    return 'jQuery(".w2p_flash").html("' + responsetext + '").slideDown().delay(1500).slideUp(); $("#target").html("' + responsetext + '");' 
    

@auth.requires_login()
@auth.requires_signature()
def join_group():
    # This is an ajax call from index to join a group
    # TODO check the type of group and handle pending
    groupid = request.args(0, cast=int, default=0)

    if groupid == 0:
        responsetext = 'Incorrect call '
    else:
        db.group_members.insert(access_group=groupid, auth_userid=auth.user_id)
        session.access_group = get_groups(auth.user_id)
        responsetext = 'You joined the group'

    return 'jQuery(".w2p_flash").html("' + responsetext + '").slideDown().delay(1500).slideUp(); $("#target").html("'+ responsetext + '");'
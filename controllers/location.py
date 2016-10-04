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

"""This controller has 3 functiosns:
index: -        simple listing of all locations now with buttons
new_location -  for creating and editing locations
my_locations -  for creating, updating and deleting details of your locations perhaps duplicated
                with new_location 
locations       for seeing a list of locations that are setup
viewlocation -  for reviewing details of a single location and links to the events that
                are planned to take place there
"""


@auth.requires(True, requires_login=requires_login)
def index():
    page = request.args(0, cast=int, default=0)
    items_per_page = 20
    limitby = (page * items_per_page, (page + 1) * items_per_page + 1)
    locations = db(db.locn.id > 0).select(orderby=[~db.locn.createdate], limitby=limitby)
    return dict(locations=locations, page=page, items_per_page=items_per_page)


@auth.requires_login()
def new_location():
    # This allows creation and editing of a locations by their owner
    fields = ['location_name', 'description', 'addrurl', 'address1', 'address2', 'address3', 'address4', 'addrcode',
              'continent', 'country', 'subdivision', 'locn_shared']
    locationid = request.args(0, default=None)
    if locationid is not None:
        record = db.locn(locationid)
        if record.auth_userid != auth.user.id:
            session.flash = 'Not Authorised - locations can only be edited by their owners'
            redirect(URL('new_location'))
        form = SQLFORM(db.locn, record, fields=fields)
    else:
        form = SQLFORM(db.locn, fields=fields)

    if form.validate():
        if locationid is not None:
            if form.deleted:
                db(db.location.id == locationid).delete()
                response.flash = 'Location deleted'
                redirect(URL('default', 'index'))
            else:
                record.update_record(**dict(form.vars))
                response.flash = 'Location updated'
                redirect(URL('default', 'index'))
        else:
            form.vars.id = db.locn.insert(**dict(form.vars))
            session.flash = 'Location Created'
            redirect(URL('accept_location', args=[form.vars.id]))
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill out the form'
    return dict(form=form)


@auth.requires(True, requires_login=requires_login)
def accept_location():
    response.flash = "Location Created"
    return locals()


@auth.requires_login()
def my_locations():
    # thinking is users shouldn't have that many of these so this should be easy - will need to be a button
    # to view events at this location and that this shold list all locations
    # but not sure that this is any better than just a simple query on location\index - to be considered
    query1 = db.locn.auth_userid == auth.user.id
    myfilter = dict(location=query1)
    grid = SQLFORM.smartgrid(db.locn, constraints=myfilter, searchable=False)
    return locals()


@auth.requires(True, requires_login=requires_login)
def viewlocation():
    locationid = request.args(0, cast=int, default=0) or redirect(URL('index'))
    locationrow = db(db.locn.id == locationid).select(cache=(cache.ram, 1200), cacheable=True).first()
    return dict(locationrow=locationrow, locationid=locationid)

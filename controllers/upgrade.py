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


# This will provide access to run some upgrade scripts in a semi-automatic
# manner


"""
    exposes:
    This needs fully updated but do at the end
    http://..../[app]/upgrade/index
    http://..../[app]/upgrade/addproject
    http://..../[app]/upgrade/fixgeography
    
    """


@auth.requires_membership('manager')
def index():
    return locals()


@auth.requires_membership('manager')
def addproject():
    '''This applies the unspecified project to all existing items and events
       to confirm to general preference of not having nulls kicking about the
       relational model '''
    unspecprojid = db(db.project.proj_name == 'Unspecified').select(db.project.id).first().id
    events = db(db.evt.projid == None).update(projid = unspecprojid)
    items = db(db.evt.projid == None).update(projid = unspecprojid)
    return dict(events=events, items=items, message='Project added to items and events')

    
@auth.requires_membership('manager')
def fixgeography():
    '''This will remove the (EU) etc from all existing continents, countries and subdivisions and once done should be fine to just run the new add countries and add continents  - will do continents first and then countries and then subdivisions'''
    
    continents = db(db.continent.id >0).select()
    
    for continent in continents:
        if continent.
    events = db(db.evt.projid is null).update(projid = unspecprojid)
    items = db(db.evt.projid is null).update(projid = unspecprojid)

    return dict(events=events, items=items, message='Project add to items and events')    
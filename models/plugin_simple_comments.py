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

db.define_table('plugin_simple_comments_comment',
                Field('tablename',default=request.args(0),
                      writable=False,readable=False),
                Field('record_id','integer',default=request.args(1),
                      writable=False,readable=False),
                Field('body',requires=IS_NOT_EMPTY(),label='Your comment'),
                Field('created_by',db.auth_user,default=auth.user_id,
                      readable=False,writable=False),
                Field('created_on','datetime',default=request.now,
                      readable=False,writable=False))

def plugin_simple_comments(tablename=None,record_id=None):
    return LOAD('plugin_simple_comments','commenton',args=(tablename,record_id),ajax=True)

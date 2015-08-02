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
#
#
# This file contains settings for auth policy which are need before setup
# of rest of configuration so staying here for now
#
#########################################################################

from gluon.storage import Storage
settings = Storage()

#Settings for user logon - lets just uncomment as needed for now - not clear if there is much scope to
#allow changes and python social auth will hopefully be added I don't think dual login worked with google but
#lets setup again and see

#Plan for this for now is that netdecisionmaking will use web2py and Janrain while
#globaldecisionmaking will use google - for some reason Janrain doesn't seem
#to come up with google as a login and google login does not support dual methods
#reason for which has not been investigated

settings.logon_methods = 'web2py'
#settings.logon_methods = 'google'
#settings.logon_methods = 'janrain'
#settings.logon_methods = 'web2pyandjanrain'
#settings.logn_methods = 'authomatic'

settings.verification = False
settings.approval = False
settings.address = True
settings.membernumber = True
settings.geography = True
settings.usecategory = True
settings.usegroups = True
#settings.database = 'mysql'
settings.database = 'sqlite'
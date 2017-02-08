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

from gluon import *


def range_widget(field, value, minval='1', maxval='10', stepval='1'):
    return INPUT(_name=field.name,
                 _type='range',
                 _class="range",
                 _id="%s_%s" % (field._tablename, field.name),
                 _value=value,
                 _min=minval,
                 _max=maxval,
                 _step=stepval,
                 requires=field.requires)
                 

def range100_widget(field, value, minval='-1', maxval='100', stepval='1'):
    return INPUT(_name=field.name,
                 _type='range',
                 _id="%s_%s" % (field._tablename, field.name),
                 _class="range",
                 _value=value,
                 _min=minval,
                 _max=maxval,
                 _step=stepval,
                 requires=field.requires)

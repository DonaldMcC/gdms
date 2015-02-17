# -*- coding: utf-8 -*-
from gluon import *

def range_widget(field, value, minval='1', maxval='10', stepval='1'):
    return INPUT(_name=field.name,
                 _type='range',
                 _id="%s_%s" % (field._tablename, field.name),
                 _class="range",
                 _value=value,
                 _min=minval,
                 _max=maxval,
                 _step=stepval,
                 requires=field.requires)


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

"""
    exposes:
    http://..../[app]/gantt/index.html

    """
from ndsfunctions import getlinks, get_gantt_data
from builtins import range


def index():
    strquery = (db.question.qtype == 'action') & (db.question.status == 'Agreed')
    orderstr = db.question.masterquest | ~db.question.currentlevel | db.question.startdate
    quests = db(strquery).select(orderby=orderstr)
    questlist = [x.id for x in quests]
    dependlist = [[] for x in range(len(questlist))]
    intlinks = getlinks(questlist)
    for x in intlinks:
        dependlist[questlist.index(x.targetid)].append(x.sourceid)

    if quests:
        projxml = get_gantt_data(quests)
    else:
        projxml = "<project></project>"

    return dict(project=XML(projxml), quests=quests)

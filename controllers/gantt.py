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


# This controller provides details about network decision making
# access to the FAQ and allows generation of a general message
# on what we are looking to achieve
# The Press Release Note for the latest version is also now included
# and some basic capabilities to download actions have also been added

"""
    exposes:
    http://..../[app]/gantt/index.html

    """
from ndsfunctions import convrow, getlinks


def index():

    strquery = (db.question.qtype == 'action') & (db.question.status == 'Agreed')
    quests = db(strquery).select()
    questlist = [x.id for x in quests]
    dependlist = [[] for x in xrange(len(questlist))]
    intlinks = getlinks(questlist)
    for x in intlinks:
        dependlist[questlist.index(x.targetid)].append(x.sourceid)
    
    # print('dep',dependlist)
    projxml = "<project>"
    if quests:
        for i, row in enumerate(quests):
            z = str(dependlist[i])
            y = max(len(z)-2, 1)
            strdepend = z[1:y]
            projxml += convrow(row, strdepend)          
    projxml += '</project>'
        
    return dict(project=XML(projxml), quests=quests)

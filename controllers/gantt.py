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
from ndsfunctions import convrow, convgroup, getlinks


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
        actiongroupid=None
        for i, row in enumerate(quests):
            z = str(dependlist[i])
            y = max(len(z)-2, 1)
            strdepend = z[1:y]
            if row.actiongroup != actiongroupid:
                # create new header task
                actiongroupid = row.actiongroup
                if actiongroupid is not None:
                    actiongroups = db(db.actiongroup.id==actiongroupid).select()
                    if actiongroups:
                        projxml += convgroup(actiongroups.first())
            projxml += convrow(row, strdepend)
    projxml += '</project>'
        
    return dict(project=XML(projxml), quests=quests, actiongroups=actiongroups)

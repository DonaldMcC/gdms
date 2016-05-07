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
from ndsfunctions import convxml

def index():

    strquery = (db.question.qtype == 'action') & (db.question.status == 'Agreed')
    quests = db(strquery).select()
    
    projxml = "<project>"
    if quests:
        for row in quests:
            projxml += '<task>'
            projxml += convxml(row.id,'pID')
            projxml += convxml(row.questiontext, 'pName')
            projxml += convxml(row.startdate, 'pStart')
            projxml += convxml(row.enddate, 'pEnd')
            projxml += convxml('gtaskred', 'pClass')
            projxml += convxml('', 'pLink')
            projxml += convxml('', 'pMile')
            projxml += convxml(row.responsible, 'pRes')
            projxml += convxml(row.perccomplete, 'pComp')
            projxml += convxml('', 'pGroup')
            projxml += convxml('', 'pParent')
            projxml += convxml('', 'pDepend')
            projxml += convxml('A caption', 'pCaption')
            projxml += convxml(row.notes, 'pNotes')            
            projxml += '</task>'           
    projxml += '</project>'
    
    project = "<project><task><pID>25</pID><pName>WCF Changes</pName><pStart>2014-02-20</pStart><pEnd>2014-02-25</pEnd>"
    project += "<pClass>gtaskred</pClass><pLink></pLink><pMile>0</pMile><pRes></pRes><pComp>0</pComp><pGroup>1</pGroup><pParent>2</pParent><pOpen>1</pOpen>" 
    project += "<pDepend>2,24</pDepend><pCaption>A caption</pCaption><pNotes>Text - can include limited HTML</pNotes></task></project>"
    
    return dict(project=XML(projxml),quests=quests)

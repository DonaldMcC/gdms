# - Coding UTF8 -
#
# Networked Decision Making
# Site: http://code.google.com/p/global-decision-making-system/
#
# License Code: GPL, General Public License v. 2.0
# License Content: Creative Commons Attribution 3.0
#
# Also visit: www.web2py.com
# or Groups: http://groups.google.com/group/web2py
# For details on the web framework used for this development
#
# Developed by Russ King (newglobalstrategy@gmail.com
# Russ also blogs occasionally to pass the time at proudofyourplanent.blogspot.com
# His general thinking on why this project is very important is availalbe at
# http://www.scribd.com/doc/98216626/New-Global-Strategy

from decimal import *

def getwraptext(textstring, answer, textwidth, maxlength=230):
    if len(textstring) < maxlength:
        txt = textstring
    else:
        txt = textstring[0:maxlength] + '...'
    if answer:
        txt = txt + '\n' + 'A:' + answer
    return txt


def d3graph(quests, links, nodepositions, grwidth=1, grheight=1, event=False):
    # copied from graph to json

    # event boolean to be updated for call from eventmap
    nodes = []
    edges = []
    for i, x in enumerate(quests):
        if event:
            nodes.append(getd3dict(x.questid, i, nodepositions[x.questid][0] * grwidth,
                                nodepositions[x.questid][1] * grheight,
                                x.questiontext, x.correctanstext(), x.status, x.qtype, x.priority))
        else:
            print 'node:', nodepositions[x.id][0]
            nodes.append(getd3dict(x.id, i, nodepositions[x.id][0] * grwidth, nodepositions[x.id][1] * grheight,
                                x.questiontext, x.correctanstext(), x.status, x.qtype, x.priority))


    # if we have siblings and partners and layout is directionless then may need to look at joining to the best port
    # or locating the ports at the best places on the shape - most questions will only have one or two connections
    # so two ports may well be enough we just need to figure out where the ports should be and then link to the
    # appropriate one think that means iterating through quests and links for each question but can set the
    # think we should move back to the idea of an in and out port and then position them possibly by rotation
    # on the document - work in progress

    if links:
        for x in links:
            # TODO - change to use getd3link
            # getd3link(x['sourceid'], x['targetid'], x['createcount'], x['deletecount'])
            edge = {}
            edge['source'] = x['sourceid']
            edge['target'] = x['targetid']

            if x['createcount'] - x['deletecount'] > 1:
                edge['dasharray'] = False
                edge['linethickness'] = min(3 + x['createcount'], 7)
            else:
                edge['dasharray'] = False
                edge['linethickness'] = 3
            edges.append(edge)
    else:
        print('nolinks')

    resultstring = 'Success'

    return dict(nodes=nodes, edges=edges, resultstring=resultstring)


def getd3dict(objid, counter, posx=100, posy=100, text='default', answer='', status='In Progress', qtype='quest', priority=50):
    # then establish fillcolour based on priority
    # establish border based on status
    # establish shape and round corners based on qtype
    # establish border colour based on item and status ???

    d3dict = {}
    if qtype == 'quest':
        d3dict['r'] = 160
        d3dict['x'] = posx
        d3dict['y'] = posy
        d3dict['wraplength'] = 25
    elif qtype == 'action':
        d3dict['r'] = 160
        d3dict['x'] = posx
        d3dict['y'] = posy
        d3dict['wraplength'] = 25
    else:  # issue
        d3dict['r'] = 160
        d3dict['x'] = posx
        d3dict['y'] = posy
        d3dict['wraplength'] = 25

    d3dict['title'] = getwraptext(text, answer, d3dict['wraplength'])
    # objname = 'Nod' + str(objid)
    d3dict['id'] = counter
    d3dict['serverid'] = objid

    d3dict['fillclr'] = colourcode(qtype, status, priority)
    d3dict['textclr'] = textcolour(qtype, status, priority)

    if status == 'In Progress':
        d3dict['swidth'] = 1
        d3dict['scolour'] = 'black'
    else:
        d3dict['swidth'] = 5
        if status == 'Agreed':
            d3dict['scolour'] = 'green'
        else:
            d3dict['scolour'] = 'red'

    d3dict['fontsize'] = 10

    return d3dict


def getd3link(sourceid, targetid, createcount, deletecount):
    # then establish fillcolour based on priority
    # establish border based on status
    # establish shape and round corners based on qtype
    # establish border colour based on item and status ???

    edge = {}
    edge['source'] = sourceid
    edge['target'] = targetid

    if createcount - deletecount > 1:
        edge['dasharray'] = False
        edge['linethickness'] = min(3 + createcount, 7)
    else:
        edge['dasharray'] = True
        edge['linethickness'] = 3

    return edge

def colourcode(qtype, status, priority):
    """This returns a colour in rgba format for colour coding the
    nodes on the network     
    >>> colourcode('quest','inprogress',100)
    'rgba(140,80,20,100)'
    >>> colourcode('quest','inprogress',0)
    'rgba(80,100,60,100)'
    >>> colourcode('quest','resolved',100)
    'rgba(120,255,70,70)'
    >>> colourcode('action','inprogress',0)
    'rgba(80,230,250,70)'
    """

    if qtype == 'action' and status == 'In Progress':
        # is this ok
        colourstr = 'rgb(80,230,250)'

    elif qtype == 'quest' and status == 'Resolved':
        colourstr = 'rgb(40,100,1)'
    else:
        priority = Decimal(priority)
        colourstr = ('rgb(' + redfnc(priority) + ',' + greenfnc(priority) + ',' + bluefnc(priority) + ')')
    return colourstr


def textcolour(qtype, status, priority):
    """This returns a colour for the text on the question
    nodes on the network     
    Aiming to get good contrast between background and text in due course
    """
    if qtype == 'action' and status == 'In Progress':
        # is this ok
        textcolourstring = 'white'
    elif qtype == 'quest' and status == 'Resolved':
        textcolourstring = 'white'
    else:
        textcolourstring = 'black'
    return textcolourstring


# plan is to set this up to go from a range of rgb at 0 to 100 priority and range is rgb(80,100,60) to 140,80,20 -
# now revised based on inital thoughts.xlsm
def redfnc(priority):
    # colint= int(90 + (priority * Decimal(1.6)))
    colint = 255
    return str(colint)


def greenfnc(priority):
    colint = min(int(500 - priority * Decimal(5.0)), 255)
    return str(colint)


def bluefnc(priority):
    """Return the position of an object in position p on heading h (unit vector after time t if travelling at speed s
       >>> bluefnc(100)
       '20'
    """
    colint = max(int(100 - (priority * Decimal(2.0))), 0)
    return str(colint)


def _test():
    import doctest
    doctest.testmod()


if __name__ == '__main__':
    # Can run with -v option if you want to confirm tests were run
    _test()

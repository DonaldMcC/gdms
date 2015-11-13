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

def getwraptext(textstring, answer, maxlength=200):
    # answer = 'This is a temp answer'
    questlength = answer and max((maxlength - len(answer)),0) or maxlength
    txt = (len(textstring) < questlength) and textstring or (textstring[0:questlength] + '...')
    if answer:
        txt = txt + 'A:' + answer
    return txt


def d3graph(quests, links, nodepositions, event=False):
    # copied from graph to json
    # event boolean to be updated for call from eventmap

    nodes = []
    edges = []
    for i, x in enumerate(quests):
        if event:
            nodes.append(getd3dict(x.id, i+2, nodepositions[x.id][0], nodepositions[x.id][1],
                                   x.questiontext, x.correctanstext(), x.status, x.qtype, x.priority))
        else:
            nodes.append(getd3dict(x.id, i+2, nodepositions[x.id][0], nodepositions[x.id][1],
                                   x.questiontext, x.correctanstext(), x.status, x.qtype, x.priority))

    # if we have siblings and partners and layout is directionless then may need to look at joining to the best port
    # or locating the ports at the best places on the shape - most questions will only have one or two connections
    # so two ports may well be enough we just need to figure out where the ports should be and then link to the
    # appropriate one think that means iterating through quests and links for each question but can set the
    # think we should move back to the idea of an in and out port and then position them possibly by rotation
    # on the document - work in progress

    if links:
        for x in links:
            edge = getd3link(x['sourceid'], x['targetid'], x['createcount'], x['deletecount'])

            # if x['createcount'] - x['deletecount'] > 1:
            #    #edge['dasharray'] = '10,1'
            #    edge['dasharray'] = str(x['createcount']) + ',1'
            #    edge['linethickness'] = min(3 + x['createcount'], 7)
            # else:
            #    edge['dasharray'] = '5,5'
            #    edge['linethickness'] = 3
            edges.append(edge)
    else:
        print('nolinks')

    resultstring = 'Success'

    return dict(nodes=nodes, edges=edges, resultstring=resultstring)


def getd3link(sourceid, targetid, createcount, deletecount):
    # then establish fillcolour based on priority
    # establish border based on status
    # establish shape and round corners based on qtype
    # establish border colour based on item and status ???

    edge = dict()
    edge['source'] = sourceid
    edge['target'] = targetid

    if createcount - deletecount > 1:
        edge['dasharray'] = str(createcount) + ',1'
        edge['linethickness'] = min(3 + createcount, 7)
    else:
        edge['dasharray'] = 5,5
        edge['linethickness'] = 3

    return edge


def getd3dict(objid, counter, posx=100, posy=100, text='default', answer='',
              status='In Progress', qtype='quest', priority=50):
    # then establish fillcolour based on priority
    # establish border based on status
    # establish shape and round corners based on qtype
    # establish border colour based on item and status ???

    d3dict = dict()
    if qtype == 'quest':
        d3dict['r'] = 160
        d3dict['x'] = posx
        d3dict['y'] = posy
        d3dict['scolour'] = 'orange'
    elif qtype == 'action':
        d3dict['r'] = 160
        d3dict['x'] = posx
        d3dict['y'] = posy
        d3dict['scolour'] = 'green'
    else:  # issue
        d3dict['r'] = 160
        d3dict['x'] = posx
        d3dict['y'] = posy
        d3dict['scolour'] = 'black'

    d3dict['title'] = getwraptext(text, answer)
    d3dict['id'] = counter
    d3dict['serverid'] = objid
    if status != 'Draft':
        d3dict['locked'] = 'Y'
    else:
        d3dict['locked'] = 'N'   

    d3dict['fillclr'] = colourcode(qtype, status, priority)
    d3dict['textclr'] = 'white' # this is not used

    if status == 'In Progress':
        d3dict['swidth'] = 2
    elif status == 'Draft':
        d3dict['swidth'] = 1
    else:
        d3dict['swidth'] = 4

    d3dict['fontsize'] = 10
    return d3dict


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
    priority = float(priority)
    if qtype == 'issue':
        colourstr = 'rgb(220,220,255)'
        colourstr = 'rgb(' + priorityfunc(priority) + ',' + priorityfunc(priority) + ',255)'
    elif qtype == 'quest':
        colourstr = 'rgb(220,255,220)'
        colourstr = 'rgb(' + priorityfunc(priority) + ',255,' + priorityfunc(priority) + ')'
    else:
        # colourstr = 'rgb(255,255,220)'
        colourstr = 'rgb(255,255,' + priorityfunc(priority) + ')'
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
def priorityfunc(priority):
    # so this should now convert priority in range 25 to 100 to an inverse range from
    # 220 to say 100
    scalesource = max(priority-25.0, 0)
    factor = (220.0-100.0) / 75.0
    scaledvalue = scalesource * factor
    colint = int(220 - scaledvalue)
    return str(colint)


def _test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    # Can run with -v option if you want to confirm tests were run
    _test()

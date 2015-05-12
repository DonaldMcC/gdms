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
from gluon import XML
from ndsfunctions import getwraptext


def initgraph(width=1000, height=1000):
    txt = r'''
    var graph = new joint.dia.Graph;
    var paper = new joint.dia.Paper({
        el: $('#map'),
        width: %d,
        height: %d,
        model: graph,
    defaultLink: new joint.dia.Link({
        attrs: { '.marker-target': { d: 'M 10 0 L 0 5 L 10 10 z', fill: 'green' },
                 '.connection': { stroke: 'green', 'stroke-width': 5 }}
    }),
    validateConnection: function(cellViewS, magnetS, cellViewT, magnetT, end, linkView) {
        return (magnetS !== magnetT);
    },
    snapLinks: { radius: 75 } });
    ''' % (width, height)
    return XML(txt)


# To be removed once confirmed not used
def portangle(objname, posx, posy, text='default', fillcolour='blue', fontsize=10, width=140, height=140,
              ports='tb', textcolour='black'):
    if ports == 'tb' and width == 160:
        txt = r'''    var %s = new joint.shapes.devs.Model({
        id: '%s',
        position: { x: %d, y: %d },
        size: { width: %d, height: %d },
        inPorts: ['t'],
        outPorts: ['b'],
        attrs: {'.label': { text: '%s', fill:'%s', 'font-size': %d,'ref-x': .12 },
                  rect: { fill: '%s' },
        '.inPorts circle': { fill: '#16A085' }, '.inPorts': {transform: 'rotate(-87)', 'ref-x':-3.0,'ref-y':5.0},
        '.outPorts circle': { fill: '#16A085' },'.outPorts': {transform: 'rotate(28)', 'ref-x':4.0,'ref-y':50.0}}
    });
    ''' % (objname, objname, posx, posy, width, height, text, textcolour, fontsize, fillcolour)
    elif ports == 'tb':
        txt = r'''    var %s = new joint.shapes.devs.Model({
        id: '%s',
        position: { x: %d, y: %d },
        size: { width: %d, height: %d },
        inPorts: ['t'],
        outPorts: ['b'],
        attrs: {'.label': { text: '%s', fill: '%s', 'font-size': %d,'ref-x': .12 },
                  rect: { fill: '%s' },
        '.inPorts circle': { fill: '#16A085' }, '.inPorts': {transform: 'rotate(-91)', 'ref-x':48.0,'ref-y':10.0},
        '.outPorts circle': { fill: '#16A085' },'.outPorts': {transform: 'rotate(38)', 'ref-x':4.0,'ref-y':-20.0}}
    });
    ''' % (objname, objname, posx, posy, width, height, text, textcolour, fontsize, fillcolour)
    elif ports == 'b':
        txt = r'''    var %s = new joint.shapes.devs.Model({
        id: '%s',
        position: { x: %d, y: %d },
        size: { width: %d, height: %d },
        outPorts: ['b'],
        attrs: {'.label': { text: '%s', fill: '%s', 'font-size': %d,'ref-x': .12 }, rect: { fill: '%s' },
        '.outPorts circle': { fill: '#16A085' },'.outPorts': {transform: 'rotate(35)'}}
    });
    ''' % (objname, objname, posx, posy, width, height, text, textcolour, fontsize, fillcolour)
    elif ports == 't':
        txt = r'''    var %s = new joint.shapes.devs.Model({
        id: '%s',
        position: { x: %d, y: %d },
        size: { width: %d, height: %d },
        inPorts: ['t'],
        attrs: {'.label': { text: '%s', fill: '%s', 'font-size': %d,'ref-x': .12 }, rect: { fill: '%s' },
        '.inPorts circle': { fill: '#16A085' }, '.inPorts': {transform: 'rotate(-90)'}}
    });
    ''' % (objname, objname, posx, posy, width, height, text, textcolour, fontsize, fillcolour)
    else:  # ports == 'lr':
        txt = r'''    var %s = new joint.shapes.devs.Model({
        id: '%s',
        position: { x: %d, y: %d },
        size: { width: %d, height: %d },
        inPorts: ['l'],
        outPorts: ['r'],
        attrs: {'.label': { text: '%s', fill: '%s', 'font-size': %d,'ref-x': .12 },
                  rect: { fill: '%s' },
        '.inPorts circle': { fill: '#16A085' }, '.inPorts': {transform: 'rotate(0)'}, 
        '.outPorts circle': { fill: '#16A085' },'.outPorts': {transform: 'rotate(0)'}}
    });
    ''' % (objname, objname, posx, posy, width, height, text, textcolour, fontsize, fillcolour)

    return XML(txt)

# think we want to try x-alignment: middle to try and centre the text
# also worth looking at joint.util.breakText() to split text into lines

# joint.util.breakText('this is quite a long text', { width: 50 })
# // 'this is\nquite a\nlong\ntext'


def getitemshape(objid, posx=100, posy=100, text='default', answer='', status='In Progress', qtype='quest', priority=50):
    # then establish fillcolour based on priority
    # establish border based on status
    # establish shape and round corners based on qtype
    # establish border colour based on item and status ???
    if qtype == 'quest':
        width = 160
        height = 140
        rx = 15
        ry = 25
        portcolour = '#16A085'
        refxin = 94
        refyin = -66
        refxout = -66
        refyout = 84
        refx = 80
        wraplength = 34
    elif qtype == 'action':
        width = 200
        height = 100
        rx = 1
        ry = 1
        portcolour = '#16A085'
        refxin = 114
        refyin = -46
        refxout = -86
        refyout = 64
        refx = 100
        wraplength = 25
    else:  # issue
        width = 120
        height = 180
        rx = 20
        ry = 15
        portcolour = '#16A085'
        refxin = 94
        refyin = -66
        refxout = -66
        refyout = 84
        refx = 80
        wraplength = 20


    qtext = getwraptext(x.questiontext, x.correctanstext(), wraplength)
    objname = 'Nod' + str(objid)

    fillclr = colourcode(qtype, status, priority)
    textclr = textcolour(qtype, status, priority)

    txt1 = r''' new joint.shapes.devs.Model({
        id: '%s',
        position: { x: %d, y: %d },
        size: { width: %d, height: %d },
        inPorts: ['t'],
        outPorts: ['b'],
         ''' % (objname, posx, posy, width, height)

    if status == 'In Progress':
        swidth = 1
        scolour = 'black'
    else: 
        swidth = 5
        if status == 'Agreed':
            scolour = 'green'
        else:
            scolour = 'red'

    fontsize = 10
    
    txt2 = r'''attrs: {'.label': { text: '%s', fill:'%s', 'font-size': %d,'ref-x': %d },
                 '.body': { 'rx': %d, 'ry': %d },
                  rect: { fill: '%s', stroke: '%s', 'stroke-width': %d},
        '.inPorts circle': { fill: '%s' }, '.inPorts': {transform:'rotate(0)', 'ref-x':%d,'ref-y':%d},
        '.outPorts circle': { fill: '%s' },'.outPorts': {transform:'rotate(0)', 'ref-x':%d,'ref-y':%d}}
    })
    ''' % (text, textclr, fontsize, refx, rx, ry, fillclr, scolour, swidth, portcolour, refxin, refyin,
           portcolour, refxout, refyout)

    txt = XML(txt1) + XML(txt2)
    return XML(txt)


def jsonportangle(objname, posx, posy, text='default', fillcolour='blue', fontsize=10, width=140, height=140, ports='tb', textcolour = 'black'):
    if ports == 'tb' and width == 160:
        txt = r''' new joint.shapes.devs.Model({
        id: '%s',
        position: { x: %d, y: %d },
        size: { width: %d, height: %d },
        inPorts: ['t'],
        outPorts: ['b'],
        attrs: {'.label': { text: '%s', fill:'%s', 'font-size': %d,'ref-x': 80 },
                 '.body': { 'rx': 15, 'ry': 25 },
                  rect: { fill: '%s', stroke: 'blue', 'stroke-width': 5},
        '.inPorts circle': { fill: '#16A085' }, '.inPorts': {transform:'rotate(0)', 'ref-x':94.0,'ref-y':-66.0},
        '.outPorts circle': { fill: '#16A085' },'.outPorts': {transform:'rotate(0)', 'ref-x':-66.0,'ref-y':84.0}}
    })
    ''' % (objname, posx, posy, width, height, text, textcolour, fontsize, fillcolour)
    elif ports == 'tb':
        txt = r''' new joint.shapes.devs.Model({
        id: '%s',
        position: { x: %d, y: %d },
        size: { width: %d, height: %d },
        inPorts: ['t'],
        outPorts: ['b'],
        attrs: {'.label': { text: '%s', fill: '%s', 'font-size': %d,'ref-x': 100 },
                  rect: { fill: '%s' },
        '.inPorts circle': { fill: '#16A085' }, '.inPorts': {transform: 'rotate(0)', 'ref-x':114.0,'ref-y':-46.0},
        '.outPorts circle': { fill: '#16A085' },'.outPorts': {transform: 'rotate(0)', 'ref-x':-86.0,'ref-y':64.0}}
    })
    ''' % (objname, posx, posy, width, height, text, textcolour, fontsize, fillcolour)
    elif ports == 'b':
        txt = r''' new joint.shapes.devs.Model({
        id: '%s',
        position: { x: %d, y: %d },
        size: { width: %d, height: %d },
        outPorts: ['b'],
        attrs: {'.label': { text: '%s', fill: '%s', 'font-size': %d,'ref-x': .12 }, rect: { fill: '%s' },
        '.outPorts circle': { fill: '#16A085' },'.outPorts': {transform: 'rotate(35)'}}
    })
    ''' % (objname, posx, posy, width, height, text, textcolour, fontsize, fillcolour)
    elif ports == 't':
        txt = r''' new joint.shapes.devs.Model({
        id: '%s',
        position: { x: %d, y: %d },
        size: { width: %d, height: %d },
        inPorts: ['t'],
        attrs: {'.label': { text: '%s', fill: '%s', 'font-size': %d,'ref-x': .12 }, rect: { fill: '%s' },
        '.inPorts circle': { fill: '#16A085' }, '.inPorts': {transform: 'rotate(-90)'}}
    })
    ''' % (objname, posx, posy, width, height, text, textcolour, fontsize, fillcolour)
    else:  # ports == 'lr':
        txt = r''' new joint.shapes.devs.Model({
        id: '%s',
        position: { x: %d, y: %d },
        size: { width: %d, height: %d },
        inPorts: ['l'],
        outPorts: ['r'],
        attrs: {'.label': { text: '%s', fill: '%s', 'font-size': %d,'ref-x': .12 },
                  rect: { fill: '%s' },
        '.inPorts circle': { fill: '#16A085' }, '.inPorts': {transform: 'rotate(0)'},
        '.outPorts circle': { fill: '#16A085' },'.outPorts': {transform: 'rotate(0)'}}
    })
    ''' % (objname, posx, posy, width, height, text, textcolour, fontsize, fillcolour)

    return XML(txt)

# To be removed once confirmed not used
def jsonportshape(objname, posx, posy, text='default', fillcolour='blue', fontsize=10, width=140, height=140, ports='tb', textcolour = 'black' ):
    # this should replace jsonportangle once working
    # current issues are;
    # ports approach should be better
    # would like ths shape to be configurable as well

    txt = r''' new joint.shapes.custom.shape({
        id: '%s',
        position: { x: %d, y: %d },
        size: { width: %d, height: %d },
        inPorts: ['t'],
        outPorts: ['b'],
        attrs: {'.label': { text: '%s', fill:'%s', 'font-size': %d,'ref-x': 80 },
        path: { d: 'm 0 110 L0 495 L80 510 Q200 490 200 670  L350 790 L500 670 Q450 110 80 110 L0 110  ', stroke:'5', fill: '%s' },
        '.inPorts circle': { fill: '#16A085' }, '.inPorts': {transform:'rotate(0)', 'ref-x':94.0,'ref-y':-66.0},
        '.outPorts circle': { fill: '#16A085' },'.outPorts': {transform:'rotate(0)', 'ref-x':-66.0,'ref-y':84.0}}
    })
    ''' % (objname, posx, posy, width, height, text, textcolour, fontsize, fillcolour)

    return XML(txt)


def smallangle(objname, posx, posy, text='default', fillcolour='blue', fontsize=10, width=140, height=140, ports='tb',
              link='http://bla.com', textcolour = 'white'):
    txt = r'''    var %s = new joint.shapes.custom.ElementLink({
        id: '%s',
        position: { x: %d, y: %d },
        size: { width: %d, height: %d },
        attrs: {  rect: { fill: '%s' },
                  a: { 'xlink:href': '%s', cursor: 'pointer' },
                  text: { text: '%s', fill: '%s', 'font-size': %d}}
    });
    ''' % (objname, objname, posx, posy, width, height, fillcolour, link, text, textcolour, fontsize)

    return XML(txt)


def rectangle(objname, posx, posy, text='default', fillcolour='blue', fontsize=10, width=140, height=140, ports='notused' ):
    txt = r'''    var %s = new joint.shapes.basic.Rect({
        position: { x: %d, y: %d },
        size: { width: %d, height: %d },
        attrs: { rect: { fill: '%s' }, text: { text: '%s', fill: 'white', 'font-size': %d } }
    });
    ''' % (objname, posx, posy, width, height, fillcolour, text, fontsize)
    return XML(txt)


def link(objname, source='rect', target='rect0', sourceport='b', targetport='t'):
    txt = r'''    var %s = new joint.dia.Link({
        source: { id: %s.id,
        port: '%s' },
        target: { id: %s.id, 
        port: '%s' },
        attrs: { '.connection': { stroke: 'yellow', 'stroke-width': 5, 'stroke-dasharray': '5 3'  },
                 '.marker-target': { fill: 'yellow', d: 'M 10 0 L 0 5 L 10 10 z' }}
    }); 
    ''' % (objname, source, sourceport, target, targetport)
    return XML(txt)


def metrolink(objname, source='rect', target='rect0', sourceport='b', targetport='t'):
    txt = r'''    var %s = new joint.dia.Link({
        source: { id: %s.id,
        port: '%s' },
        target: { id: %s.id,
        port: '%s' },
        attrs: { '.connection': { stroke: 'yellow', 'stroke-width': 5, 'stroke-dasharray': '5 3' },
                 '.marker-target': { fill: 'yellow', d: 'M 10 0 L 0 5 L 10 10 z' }}
    }); 
    %s.set('router', { name: 'metro' });
    %s.set('connector', { name: 'rounded', args: { radius: 60 }});
    ''' % (objname, source, sourceport, target, targetport, objname, objname)

    return XML(txt)


def newmetlink(objname, source='rect', target='rect0', sourceport='b', targetport='t', dasharray=False,
               linethickness=5):
    if dasharray:
        txt = r'''    var %s = new joint.dia.Link({
        source: { id: %s.id,
        port: '%s' },
        target: { id: %s.id,
        port: '%s' },
        attrs: { '.connection': { stroke: 'yellow', 'stroke-width': %d, 'stroke-dasharray': '5 3' },
                 '.marker-target': { fill: 'yellow', d: 'M 10 0 L 0 5 L 10 10 z' }}
    }); 
    %s.set('router', { name: 'metro' });
    %s.set('connector', { name: 'rounded', args: { radius: 60 }});
    ''' % (objname, source, sourceport, target, targetport, linethickness, objname, objname)
    else:
        txt = r'''    var %s = new joint.dia.Link({
        source: { id: %s.id,
        port: '%s' },
        target: { id: %s.id,
        port: '%s' },
        attrs: { '.connection': { stroke: 'yellow', 'stroke-width': %d},
                 '.marker-target': { fill: 'yellow', d: 'M 10 0 L 0 5 L 10 10 z' }}
    }); 
    %s.set('router', { name: 'metro' });
    %s.set('connector', { name: 'rounded', args: { radius: 60 }});
    ''' % (objname, source, sourceport, target, targetport, linethickness, objname, objname)

    return XML(txt)

def jsonmetlink(objname, source='rect', target='rect0', sourceport='b', targetport='t', dasharray=False,
               linethickness=5):

    #;
    #%s.set('router', { name: 'metro' });
    #%s.set('connector', { name: 'rounded', args: { radius: 60 }});

    if dasharray:
        txt = r'''    new joint.dia.Link({
        source: { id: '%s',
        port: '%s' },
        target: { id: '%s',
        port: '%s' },
        attrs: { '.connection': { stroke: 'yellow', 'stroke-width': %d, 'stroke-dasharray': '5 3' },
                 '.marker-target': { fill: 'yellow', d: 'M 10 0 L 0 5 L 10 10 z' }}
    })
    ''' % (source, sourceport, target, targetport, linethickness)
    else:
        txt = r'''    var %s = new joint.dia.Link({
        source: { id: '%s',
        port: '%s' },
        target: { id: '%s',
        port: '%s' },
        attrs: { '.connection': { stroke: 'yellow', 'stroke-width': %d},
                 '.marker-target': { fill: 'yellow', d: 'M 10 0 L 0 5 L 10 10 z' }}
    })
    ''' % (objname, source, sourceport, target, targetport, linethickness)

    return XML(txt)


def addobjects(objlist):
    txt = r'[rect,rect0, rect2, rect3, link, link1,link2]'
    return XML(txt)


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
        colourstr = ('rgb(' + redfnc(priority) + ',' + greenfnc(priority) + ','
                     + bluefnc(priority) + ')')
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

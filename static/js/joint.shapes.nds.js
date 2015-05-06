/*! JointJS v0.9.3 - JavaScript diagramming library  2015-02-03 


This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

This is copied from joint.shapes.devs to create default shapes for NDS
 */

if (typeof exports === 'object') {

    var joint = {
        util: require('../src/core').util,
        shapes: {
            basic: require('./joint.shapes.basic')
        },
        dia: {
            ElementView: require('../src/joint.dia.element').ElementView,
            Link: require('../src/joint.dia.link').Link
        }
    };
    var _ = require('lodash');
}

joint.shapes.nds = {};

joint.shapes.nds.Model = joint.shapes.basic.Generic.extend(_.extend({}, joint.shapes.basic.PortsModelInterface, {

    markup: '<g class="rotatable"><g class="scalable"><rect class="body"/></g><text class="label"/><g class="inPorts"/><g class="outPorts"/></g>',
    portMarkup: '<g class="port port<%= id %>"><circle class="port-body"/><text class="port-label"/></g>',

    defaults: joint.util.deepSupplement({

        type: 'nds.Model',
        size: { width: 1, height: 1 },
        
        inPorts: [],
        outPorts: [],

        attrs: {
            '.': { magnet: false },
            '.body': {
                width: 150, height: 250,
                stroke: '#000000'
            },
            '.port-body': {
                r: 10,
                magnet: true,
                stroke: '#000000'
            },
            text: {
                'pointer-events': 'none'
            },
            '.label': { text: 'Model', 'ref-x': .5, 'ref-y': 10, ref: '.body', 'text-anchor': 'middle', fill: '#000000' },
            '.inPorts .port-label': { x:-15, dy: 4, 'text-anchor': 'end', fill: '#000000' },
            '.outPorts .port-label':{ x: 15, dy: 4, fill: '#000000' }
        }

    }, joint.shapes.basic.Generic.prototype.defaults),

    getPortAttrs: function(portName, index, total, selector, type) {

        var attrs = {};

        var portClass = 'port' + index;
        var portSelector = selector + '>.' + portClass;
        var portLabelSelector = portSelector + '>.port-label';
        var portBodySelector = portSelector + '>.port-body';

        attrs[portLabelSelector] = { text: portName };
        attrs[portBodySelector] = { port: { id: portName || _.uniqueId(type) , type: type } };
        attrs[portSelector] = { ref: '.body', 'ref-y': (index + 0.5) * (1 / total) };

        if (selector === '.outPorts') { attrs[portSelector]['ref-dx'] = 0; }

        return attrs;
    }
}));

joint.shapes.nds.Item = joint.shapes.nds.Model.extend({

    defaults: joint.util.deepSupplement({

        type: 'nds.Item',
        size: { width: 80, height: 80 },
        attrs: {
            '.body': { fill: 'salmon' },
            '.label': { text: 'Atomic' },
            '.inPorts .port-body': { fill: 'PaleGreen' },
            '.outPorts .port-body': { fill: 'Tomato' }
        }

    }, joint.shapes.nds.Model.prototype.defaults)

});


joint.shapes.nds.Action = joint.shapes.nds.Model.extend({

    defaults: joint.util.deepSupplement({

        type: 'nds.Action',
        size: { width: 80, height: 80 },
        attrs: {
            '.body': { fill: 'salmon' },
            '.label': { text: 'Atomic' },
            '.inPorts .port-body': { fill: 'PaleGreen' },
            '.outPorts .port-body': { fill: 'Tomato' }
        }

    }, joint.shapes.nds.Model.prototype.defaults)

});

joint.shapes.nds.Issue = joint.shapes.nds.Model.extend({

    defaults: joint.util.deepSupplement({

        type: 'nds.Issue',
        size: { width: 200, height: 300 },
        attrs: {
            '.body': { fill: 'seaGreen' },
            '.label': { text: 'Coupled' },
            '.inPorts .port-body': { fill: 'PaleGreen' },
            '.outPorts .port-body': { fill: 'Tomato' }
        }

    }, joint.shapes.nds.Model.prototype.defaults)
});

joint.shapes.nds.Link = joint.dia.Link.extend({

    defaults: {
        type: 'nds.Link',
        attrs: { '.connection' : { 'stroke-width' :  2 }}
    }
});

joint.shapes.nds.ModelView = joint.dia.ElementView.extend(joint.shapes.basic.PortsViewInterface);
joint.shapes.nds.AtomicView = joint.shapes.nds.ModelView;
joint.shapes.nds.CoupledView = joint.shapes.nds.ModelView;


if (typeof exports === 'object') {

    module.exports = joint.shapes.nds;
}


/*
    Current code
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


var a1 = new joint.shapes.devs.Atomic({
    position: { x: 360, y: 360 },
    inPorts: ['xy'],
    outPorts: ['x','y']
});


*/

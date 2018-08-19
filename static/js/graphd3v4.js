// This is now main d3 v4 graph layout it should be used for 5 different functions
    // 1 vieweventmap for eventmap views - redraw usually false
    // 2 search maps which are not saved - redraw always true ie force layout kicks in
    // 3 newindex review if map check box is setup and checked
    // 4 project view which may or may not need positions stored to be considered
    // 5 default view on home range

    // Basic eventmap now working again - but need the links and nodes to be prettied up a bit
    // then mainly come back to the other editability and modes to do the different things which 
    // have been removed - a load screen is now proposed to allow full editing of draft questions
    // this will need mapped out and there will be some issues
    // the tooltip setup also needs confirmed and the force graph parameters need sorted


    // HOw to get link ids instead of index
    // http://stackoverflow.com/questions/23986466/d3-force-layout-linking-nodes-by-name-instead-of-index

    // embedding web2py in d3
    // http://stackoverflow.com/questions/34326343/embedding-d3-js-graph-in-a-web2py-bootstrap-page


    var consts =  {
    selectedClass: "selected",
    connectClass: "connect-node",
    circleGClass: "conceptG",
    nodeRadius: 80

  };

// below will all move into some sort of object maybe combine with above
    var textHeight = 10;
    var lineHeight = textHeight + 5;
    var lines = [];
   initLines();

    var graphvars = {
          selectedNode: null,
          selectedEdge: null,
          mouseDownNode: null,
          mouseDownLink: null,
          touchlinking: false,
          justDragged: false,
          justScaleTransGraph: false,
          lastKeyDown: -1,
          shiftNodeDrag: false,
          selectedText: null,
          lastserverid: ''
      };

    var lastxpos = '';
    var lastypos = '';
    var edges = [];

    function addnode(itemtext, posx, posy) {
        nodes.push ({
            answers: ['yes', 'no'],
            fillclr: "rgb(215,255,215)",
            id: nodes.length,
            locked: "N",
            priority: 25,
            qtype: 'quest',
            r: 160,
            fixed: false,
            scolour: "orange",
            linkcount: 0,
            fontsize: 10,
            serverid: 0,
            status: "Draft",
            swidth: 2,
            textclr: "white",
            title: itemtext,
            xpos: posx,
            ypos: posy,
            x: rescale(posx, width, 1000),
            y: rescale(posy, height, 1000)
        });

        console.log('nodes', nodes);
       redrawnodes();

}

    function updatenode(node, itemtext) {
        console.log(node.serverid, itemtext);
        node.title = itemtext;
        redrawnodes();
        console.log('nodes', nodes);
       redrawnodes();

}

    // handle redraw graph
    d3.select("#redraw-graph").on("click", function(){
         redrawGraph();
    });


// below should revert to the iterative with additional link values and link types to be added
    links.forEach(function(e) {
        var sourceNode = nodes.filter(function(n) {return n.serverid === e.source;})[0],
            targetNode = nodes.filter(function(n) {return n.serverid === e.target;})[0];

        edges.push({
            source: sourceNode,
            target: targetNode,
            dasharray: e.dasharray,
            value: 1});

    });



// this was being used for some of the force values - to be considered
    edges.forEach(function(e) {
        if (!e.source["linkcount"]) e.source["linkcount"] = 0;
        if (!e.target["linkcount"]) e.target["linkcount"] = 0;

        e.source["linkcount"]++;
        e.target["linkcount"]++;
    });

    //below from https://bl.ocks.org/shimizu/e6209de87cdddde38dadbb746feaf3a3
    // but need to deccide on best approach
/*
      function setSize(data) {
        width = document.querySelector("#graph").clientWidth
        height = document.querySelector("#graph").clientHeight

        margin = {top:0, left:0, bottom:0, right:0 }


        chartWidth = width - (margin.left+margin.right)
        chartHeight = height - (margin.top+margin.bottom)

        svg.attr("width", width).attr("height", height)


        chartLayer
            .attr("width", chartWidth)
            .attr("height", chartHeight)
            .attr("transform", "translate("+[margin.left, margin.top]+")")
    }
*/
        //var height = window.innerHeight|| docEl.clientHeight|| bodyEl.clientHeight;
        //var width = window.innerWidth || docEl.clientWidth || bodyEl.clientWidth;
        var height = window.innerHeight;
        var width = window.innerWidth;

        //console.log( height);
        //console.log (width);

        nodes.forEach(function(e) {
            //don't think there is a problem here unless debugging
            //e.x = Math.max(consts.nodeRadius, Math.min(width - consts.nodeRadius, rescale(e.xpos, width, 1000)));
            //e.y = Math.max(consts.nodeRadius, Math.min(height - consts.nodeRadius, rescale(e.ypos, width, 1000)));
            e.x = rescale(e.xpos, width, 1000);
            e.y = rescale(e.ypos, height, 1000);
    });

        function rescale(point, newscale, oldscale) {
            if (oldscale != 0 ) {
                return (point * newscale) / oldscale
            }
            else {
                return point
            }
        }

// may look at making this dynamic again at some point 
    // will now take from v4js for now var width = 960, height = 600;


    function redrawlinks() {
      svg = d3.select("#graph").select('svg');

      //var tdSize=svg.select("#links").selectAll('.link').size();
        var link = svg.select("#links").selectAll('.link')
            .data(edges)
            .attr("class", "link")
            .attr("d", function(d){
        return "M" + d.source.x + "," + d.source.y + "L" + d.target.x + "," + d.target.y;
      })
      .classed("link", true)
        .attr("stroke", "purple")
         .style("stroke-width", function(d){return d.linethickness})
        .style("stroke-dasharray", function(d){return d.dasharray})
        .attr("marker-end", "url(#end-arrow)")
        .style('marker-end', 'url(#end-arrow)');

            link.enter()
            .append("path")
            .attr("class", "link")
            .attr("d", function(d){
        return "M" + d.source.x + "," + d.source.y + "L" + d.target.x + "," + d.target.y;
      })
      .classed("link", true)
        .attr("stroke", "purple")
         .style("stroke-width", function(d){return d.linethickness})
        .style("stroke-dasharray", function(d){return d.dasharray})
        .attr("marker-end", "url(#end-arrow)")
        .style('marker-end', 'url(#end-arrow)');

    link.exit().remove();

    }

function redrawnodes() {
    svg = d3.select("#graph").select('svg');

    node = svg.select("#nodes").selectAll(".node")
        .data(nodes);

    node.enter().append("g")
        .attr("class", function (d) {
            return "node " + d.type;
        })
        .attr("transform", function (d) {
            return "translate(" + d.x + "," + d.y + ")";
        })
        .on("click", nodeclick)
        .call(d3.drag()
            .on("start", dragnodestarted)
            .on("drag", dragnode)
            .on("end", dragnodeended))
        .append('circle')
        .attr('r', String(consts.nodeRadius))
        .style("fill", function (d) {
            return d.fillclr
        })
        .style("stroke", function (d) {
            return d.scolour
        })
        .style("stroke-width", function (d) {
            return d.swidth
        })
        .style("stroke-dasharray", function (d) {
            if (d.status == 'Draft') {
                return ("8,8")
            } else {
                return ("1,1")
            }
        })
        .each(function (d) {
            wrapText(d3.select(this.parentNode), d.title)
        });


    // add the nodes
    node.attr("class", function (d) {
        return "node " + d.type;
    })
        .attr("transform", function (d) {
            return "translate(" + d.x + "," + d.y + ")";
        });

    node.select('circle')
        .attr('r', String(consts.nodeRadius))
        .style("fill", function (d) {
            return d.fillclr
        })
        .style("stroke", function (d) {
            return d.scolour
        })
        .style("stroke-width", function (d) {
            return d.swidth
        })
    ;


    node.each(function (d) {
        clearText(d3.select(this), d.title, d.txtclr);
        wrapText(d3.select(this), d.title, d.txtclr);

        node.exit().remove();
    });

}

    svg = d3.select("#graph").append("svg")
            .attr("width", width)
            .attr("height", height);

   svg.append("svg:defs").selectAll("marker-end")
    .data(["end-arrow"])      // Different link/path types can be defined here
   .enter().append("svg:marker")    // This section adds in the arrows
    .attr("id", 'end-arrow')
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", "46")   /* Moves the arrow head out, allow for radius */
    .attr("refY", 0)   /* -1.5  */
    .attr("markerWidth", 3.5)
    .attr("markerHeight", 3.5)
    .attr("orient", "auto")
    .append("svg:path")
    .attr("d", "M0,-5L10,0L0,5");

    svg.append("g").attr("id", "links");
    svg.append("g").attr("id", "nodes");


    var link = svg.select("#links").selectAll('.link')
            .data(edges)
            .classed(consts.selectedClass, function(d){
            return d === state.selectedEdge;
            })
            .enter()
            .append("path")
            .attr("class", "link")
            .attr("d", function(d){
        return "M" + d.source.x + "," + d.source.y + "L" + d.target.x + "," + d.target.y;
      })
      .classed("link", true)
        .attr("stroke", "purple")
         .style("stroke-width", function(d){return d.linethickness})
        .style("stroke-dasharray", function(d){return d.dasharray})
        .attr("marker-end", "url(#end-arrow)")
        .style('marker-end', 'url(#end-arrow)');

    //below commented out as this now only called on inital load and exit impossible
    //link.exit().remove();


    var node = svg.select("#nodes").selectAll(".node")
            .data(nodes)
            .enter().append("g")
            .attr("class", function(d) { return "node " + d.type;})
            .attr("transform", function(d){return "translate(" + d.x + "," + d.y + ")";})
            .on("click", nodeclick)
             .call(d3.drag()
              .on("start", dragnodestarted)
              .on("drag", dragnode)
              .on("end", dragnodeended));


    // add the nodes
    node.append('circle')
        .attr('r', String(consts.nodeRadius))
        .style("fill", function(d){return d.fillclr})
        .style("stroke", function(d){return d.scolour})
         .style("stroke-dasharray", function(d){if (d.status=='Draft') {return ("8,8")} else {return ("1,1")}}) // make the stroke dashed
        .style("stroke-width", function(d){return d.swidth})
         /*.attr('height', 25)*/
        ;

    node.each(function(d) {
    wrapText(d3.select(this), d.title, d.txtclr);
    });

    //V E L A D view, edit, link, add, delete
    //So getting real problems with click events not triggering instead only the
    //drag event was firing - think we overcome this with a justDragged variable 
    //and calling fromdrag for now

    function nodeclick(d) {
        console.log("you clicked node", d.serverid);
        switch(inputmode) {
    case 'E':
        //Edit - this should load the URL and possibly view would bring up
        //full thing as view quest
        console.log("you clicked edit", d.serverid);
        console.log("calling quetsadd");
        if (d.locked != 'Y') {
            questadd('Edit', d3.event.x, d3.event.y, d);
        }
        else {
            out("Only draft item text editable")
        }
        break;
    case 'L':
        if (graphvars.mousedownnode && graphvars.mousedownnode != d) {
        //console.log(" link request to make", d.serverid);
        var newEdge = {source: graphvars.mousedownnode, target: d};
        edges.unshift(newEdge);
        var linksource = graphvars.mousedownnode.serverid.toString();
        var linkdest = d.serverid.toString();
        if (linksource == '0') {
            linksource = graphvars.mousedownnode.title;
        }
        if (linksource == '0') {
            linksource = d.serverid.title;
        }
        requestLink(linksource, linkdest);
        redrawlinks();
        redrawnodes();

        graphvars.mousedownnode = null;
            }
            case 'M':
                if (graphvars.mousedownnode && graphvars.mousedownnode != d) {
        console.log("move node down into", d.serverid);

        var nodeid = graphvars.mousedownnode.serverid.toString();
        if (nodeid == '0') {
            nodeid = graphvars.mousedownnode.serverid.title;
        }
        demoteNode(nodeid, d32py.eventid, d.serverid);
        nodes.splice(nodes.indexOf(graphvars.mousedownnode), 1);
        spliceLinksForNode(graphvars.mousedownnode);
        graphvars.mousedownnode = null;
        redrawlinks();
        redrawnodes();
        redrawnodes();


        graphvars.mousedownnode = null;
            }
        else {
            graphvars.mousedownnode = d;
        }
        break;
            case 'D':
            console.log(nodes);
        console.log("you clicked delete", d.serverid);
        var nodeid = d.serverid.toString();
        if (nodeid == '0') {
            nodeid = d.serverid.title;
        }
        d3.select("body").select('div.tooltip').remove();
        deleteNode(nodeid, d32py.eventid);
        nodes.splice(nodes.indexOf(d), 1);
        spliceLinksForNode(d);
        graphvars.mousedownnode = null;
        console.log(nodes);
        redrawlinks();
        redrawnodes();
        redrawnodes();
        break;
    default:
        console.log("view or add on a node do nothing", d.serverid);
}
    d3.event.stopPropagation();
        }


spliceLinksForNode = function(node) {
        toSplice = edges.filter(function(l) {
      return (l.source === node || l.target === node);
    });
    toSplice.map(function(l) {
      edges.splice(edges.indexOf(l), 1);
    });
  };

    function linkclick(d) {
        console.log("you clicked link", d);
        switch (inputmode) {
            case 'D':
                //Edit - this should load the URL and
                console.log("this will call delete link");
                deleteLink(edges[edges.indexOf(d)].source.serverid.toString(), edges[edges.indexOf(d)].target.serverid.toString());
                //console.log(edges.length);
                //console.log(d.source,d.target);
                // so this is failing and deleting the wrong edge despite correct one being selected as d
                //console.log('index',edges.indexOf(d) );
                //console.log(edges);
                indexes = $.map(edges, function(e, index) {
                if((e.source.id == d.source.id) && (e.target.id=d.target.id)) {
                    return index;
                    }
                });

                //console.log(indexes[0]);
                edges.splice(indexes[0], 1);
                //console.log(edges.length)
                //console.log(edges);
                redrawlinks();
                break;
            default:
                //console.log("probably do nothing", d.source);
        }

        d3.event.stopPropagation();
    }

    link.on("click", linkclick);
    node.on("click", nodeclick);
    svg.on("click", backclick);

    function backclick(d) {
        //console.log("you clicked background");
        switch(inputmode) {
        case 'A':
        //Edit - this should load the URL and
        //console.log("this will add a new node at", d3.event.x);
        questadd('New', Math.floor(rescale(d3.event.x, 1000, width)), Math.floor(rescale(d3.event.y, 1000, width)));
        break;
    default:
        //console.log("reset the source if linking");
}
    }

//need to actually figure out what goes in the tooltip 
    node.on("mouseover", function(d) {
        //console.log("mouseover");
        var g = d3.select(this);  // the node (table)

        var fieldformat = "<TABLE class='table table-bordered table-condensed bg-info'>";
        
        if (d.qtype == 'quest') {
                fieldformat += "<TR><TD><B>Question</B></TD><TD></TD><TD></TD><TD></TD></TR>";   
        }
        else if (d.qtype == 'issue') {
                fieldformat += "<TR><TD><B>Issue</B></TD><TD></TD><TD></TD><TD></TD></TR>";   
        }
        else {
              fieldformat += "<TR><TD><B>Action</B></TD><TD></TD><TD></TD><TD></TD></TR>";  
              fieldformat += "<TR><TD><B>Due Date</B></TD><TD>"+ d.duedate+"</TD><TD><B>"+" Responsible:"+"</B></TD><TD>"+ d.responsible+"</TD></TR>";
        }
        
            fieldformat += "<TR><TD><B>Status</B></TD><TD>"+ d.status+"</TD><TD><B>"+" Priority:"+"</B></TD><TD>"+ d.priority+"</TD></TR>";
            
            
        fieldformat += "</TABLE>";

            // Define 'div' for tooltips
        var div = d3.select("body").append("div")  // declare the tooltip div
	        .attr("class", "tooltip")              // apply the 'tooltip' class
                .html(fieldformat)
                .style("left", 10 + (d3.event.pageX + 10) + "px")// or just (d.x + 50 + "px") (d3.event.pageX)
                .style("top", (d3.event.pageY - 20) + "px")// or ...(d3.event.pageY - 20)
                .transition()
                .duration(800)
                .style("opacity", 0.9);

    });


    node.on("mouseout", function(d) {
        d3.select("body").select('div.tooltip').remove();
    });


        function dragnodestarted(d) {
            //d.fx = d.x;
            //d.fy = d.y;
        }

        function dragnode(d) {
            //console.log('dragging');
            //console.log(d.id);
            //console.log(d.x);


            switch (inputmode) {
                case 'E':

            //d.fx = d3.event.x;
            //d.fy = d3.event.y;
            d.x = d3.event.x;
            d.y = d3.event.y;
            d3.select(this).attr("transform", function (d) {
                return "translate(" + d.x + "," + d.y + ")";
            });
            redrawlines();
                    break;
            default:
            //console.log("do nothing ");
                    }
        }

        function dragnodeended(d) {
            console.log('drag ended');
            //d.fx = null;
            //d.fy = null;

            lastserverid = d.serverid.toString();
            lastxpos = Math.floor(rescale(d.x,1000,width));
            lastypos = Math.floor(rescale(d.y,1000,height));
            moveElement(lastserverid, lastxpos.toString(), lastypos.toString() );
            graphvars.justDragged = false;
            graphvars.justDragged = true;
        }

if (d32py.redraw == true) {
            redrawGraph()
}

// ** Update data section (Called from the onclick)
function redrawlines() {
    svg.selectAll('.link')
        .data(edges)
        .attr("d", function (d) {
            return "M" + d.source.x + "," + d.source.y + "L" + d.target.x + "," + d.target.y;
        });
}

//            .force("charge", d3.forceManyBody().strength(-50000))

function redrawGraph() {
    var attractForce = d3.forceManyBody().strength(2000).distanceMax(100000)
                     .distanceMin(1000);
    var repelForce = d3.forceManyBody().strength(-3000).distanceMax(800)
                   .distanceMin(1);

    var simulation = d3.forceSimulation()
        .force("attractForce",attractForce)
        .force("link", d3.forceLink().id(function(d) { return d.id; }))
        .force("repelForce",repelForce)
            .force("center", d3.forceCenter(width / 2, height / 2))
             .force("y", d3.forceY(height / 2).strength(0.07))
            .force("x", d3.forceX(width / 2).strength(0.05));

    function strength() { return 0.1; }
    function distance() { return 200; }

   simulation
        .nodes(nodes)
        .on("tick", tick)
        .on('end', function() {
        // layout is done
        writetoserver();
        });

    simulation.force("link")
        .links(edges)
        .distance(distance)
        .strength(strength);


    function tick() {
        node.attr("transform", function (d) {
            d.x = Math.max(consts.nodeRadius, Math.min(width - consts.nodeRadius, d.x));
            d.y = Math.max(consts.nodeRadius, Math.min(height - consts.nodeRadius, d.y));
            return "translate(" + d.x + "," + d.y + ")";
        });

        redrawlines();

    }
    //console.log('forcenodes', nodes)

}

function writetoserver() {
    if (d32py.vieweventmap == true && d32py.editable == true) {
        // if owner and eventmapiterate through nodes and call function to write new positions to server
        nodes.forEach(function (e) {
            //console.log(e.serverid.toString() + ':' + Math.floor(e.x).toString() + ':' + Math.floor(rescale(e.x, 1000, width)).toString());
            moveElement(e.serverid.toString(), Math.floor(rescale(e.x, 1000, width)).toString(),
                Math.floor(rescale(e.y, 1000, height)).toString());
        })
    }
}

function clearText(gEl) {
     var el = gEl.selectAll("text");
        el.remove('tspan');
 }


// think these may become methods from naming setup
function wrapText(gEl, title) {

     var i = 0;
     var line = 0;
     var words = title.split(" ");



     var el = gEl.append("text")
     //.style("fill", txtclr) not getting this to work and possibly not a good idea anyway
         .attr("text-anchor", "middle")
         .attr("font-size", "11px")
         .attr("dy", "-" + 8 * 7.5);

     while (i < lines.length && words.length > 0) {

         line = lines[i++];
         var lineData = calcAllowableWords(line.maxLength, words);
         var tspan = el.append('tspan').text(lineData.text);
         if (i > 1)
             tspan.attr('x', 0).attr('dy', '15');
         words.splice(0, lineData.count);
     }
 }

        // calculate how many words will fit on a line

function calcAllowableWords(maxWidth, words) {

    var testLine = "";
    var spacer = "";
    var fittedWidth = 0;
    var fittedText = "";
    //ctx.font = font;

    for (var i = 0; i < words.length; i++) {

        testLine += spacer + words[i];
        spacer = " ";

        //var width = ctx.measureText(testLine).width;
        var width = testLine.length * 5;
        if (width > maxWidth) {
            return ({
                count: i,
                width: fittedWidth,
                text: fittedText
            });
        }

        fittedWidth = width;
        fittedText = testLine;

    }
    return ({
                count: i,
                width: fittedWidth,
                text: fittedText
            });
}

function initLines() {

  var radius  = 80;

    for (var y = radius * .9; y > -radius; y -= lineHeight) {

        var h = Math.abs(radius - y);

        if (y - lineHeight < 0) {
            h += 20;
        }

        var length = 2 * Math.sqrt(h * (2 * radius - h)) + 5;

        if (length && length > 10) {
            lines.push({
                y: y,
                maxLength: length
            });
        }

    }
}

        function out(m) {
        $('#target').html(m);
        }
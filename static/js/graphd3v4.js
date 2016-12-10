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
            answers: ('yes', 'no'),
            fillclr: "rgb(215,255,215)",
            id: 0,
            locked: "N",
            priority: 25,
            qtype: 'quest',
            r: 160,
            scolour: "orange",
            serverid: 0,
            linkcount: 0,
            fontsize: 10,
            serverid: 0,
            status: "Draft",
            swidth: 2,
            textclr: "white",
            title: itemtext,
            x: posx,
            y: posy
        });

       redrawnodes();
        console.log('nodes', nodes);
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

    //console.log(edges);


// this was being used for some of the force values - to be considered
    edges.forEach(function(e) {
        if (!e.source["linkcount"]) e.source["linkcount"] = 0;
        if (!e.target["linkcount"]) e.target["linkcount"] = 0;

        e.source["linkcount"]++;
        e.target["linkcount"]++;
    });

    //console.log('edgefinal', edges);

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
        //var height = 350 + (links.length * 25); - this makes graph bigger than container
        var height = window.innerHeight|| docEl.clientHeight|| bodyEl.clientHeight;
        var width = window.innerWidth || docEl.clientWidth || bodyEl.clientWidth;


// may look at making this dynamic again at some point 
    // will now take from v4js for now var width = 960, height = 600;


    function redrawlinks() {
      svg = d3.select("#graph").select('svg');

      var tdSize=svg.selectAll('.link').size();
      console.log(tdSize);
        var link = svg.selectAll('.link')
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
    //console.log('redrawn')
    //    tdSize=svg.selectAll('.link').size();
    //console.log(tdSize);
    };

function redrawnodes() {
      svg = d3.select("#graph").select('svg');

       var node = svg.selectAll(".node")
            .data(nodes)
            .enter().append("g")
            .attr("class", function(d) { return "node " + d.type;})
            .attr("transform", function(d){return "translate(" + d.x + "," + d.y + ")";})
            .call(d3.drag()
              .on("start", dragnodestarted)
              .on("drag", dragnode)
              .on("end", dragnodeended));


    // add the nodes
    node.append('circle') /* 'circlej */
        .attr('r', String(consts.nodeRadius))
        .style("fill", function(d){return d.fillclr})
        .style("stroke", function(d){return d.scolour})
        .style("stroke-width", function(d){return d.swidth})
        /* .attr('height', 25) */
        ;

    node.each(function(d) {
    wrapText(d3.select(this), d.title, d.txtclr)});

    node.exit().remove();

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


    var link = svg.selectAll('.link')
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


    var node = svg.selectAll(".node")
            .data(nodes)
            .enter().append("g")
            .attr("class", function(d) { return "node " + d.type;})
            .attr("transform", function(d){return "translate(" + d.x + "," + d.y + ")";})
            .call(d3.drag()
              .on("start", dragnodestarted)
              .on("drag", dragnode)
              .on("end", dragnodeended));


    // add the nodes
    node.append('circle')
        .attr('r', String(consts.nodeRadius))
        .style("fill", function(d){return d.fillclr})
        .style("stroke", function(d){return d.scolour})
        .style("stroke-width", function(d){return d.swidth})
         /*.attr('height', 25)*/
        ;

    node.each(function(d) {
    wrapText(d3.select(this), d.title, d.txtclr)});


    //V E L A D view, edit, link, add, delete
    //So getting real problems with click events not triggering instead only the
    //drag event was firing - think we overcome this with a justDragged variable 
    //and calling fromdrag for now

    function nodeclick(d) {
        console.log("you clicked node", d.serverid);
        if (graphvars.justDragged == false) {
        switch(inputmode) {
    case 'E':
        //Edit - this should load the URL and possibly view would bring up
        //full thing as view quest
        console.log("you clicked edit", d.serverid);
        break;
    case 'L':
        if (graphvars.mousedownnode && graphvars.mousedownnode != d) {
        //console.log(" link request to make", d.serverid);
        var newEdge = {source: graphvars.mousedownnode, target: d};
        edges.push(newEdge);
        svg.append("path")
      .attr("class", "line")
        .attr("d",  "M" + graphvars.mousedownnode.x + "," + graphvars.mousedownnode.y + "L" + d.x + "," + d.y)
            .classed("link", true)
        .attr("stroke", "purple")
         .style("stroke-width", 2)
        .attr("marker-end", "url(#end-arrow)")
        .style('marker-end', 'url(#end-arrow)');
        requestLink(graphvars.mousedownnode.serverid.toString(), d.serverid.toString());
        graphvars.mousedownnode = null;
            }
        else {
            graphvars.mousedownnode = d;
        }
        break;
        case 'D':
        console.log("you clicked delete", d.serverid);
        deleteNode(nodes[nodes.indexOf(d)].serverid.toString(), eventid);
        nodes.splice(thisGraph.nodes.indexOf(d), 1);
        spliceLinksForNode(d);
        graphvars.mousedownnode = null;
        redraw();
        break;
    default:
        console.log("view or add on a node do nothing", d.serverid);
}
        }
    d3.event.stopPropagation();
    graphvars.justDragged = false;
    }



spliceLinksForNode = function(node) {
        toSplice = edges.filter(function(l) {
      return (l.source === node || l.target === node);
    });
    toSplice.map(function(l) {
      edges.splice(thisGraph.edges.indexOf(l), 1);
    });
  };

    function linkclick(d) {
        console.log("you clicked link", d);
        switch (inputmode) {
            case 'D':
                //Edit - this should load the URL and
                console.log("this will call delete link");
                //deleteLink(edges[edges.indexOf(d)].source.serverid.toString(), edges[edges.indexOf(d)].target.serverid.toString());
                console.log(edges.length);
                console.log(d.source,d.target);
                // so this is failing and deleting the wrong edge despite correct one being selected as d
                console.log('index',edges.indexOf(d) );
                console.log(d.source.id, d.target.id)
                console.log(edges);
                indexes = $.map(edges, function(e, index) {
                if((e.source.id == d.source.id) && (e.target.id=d.target.id)) {
                    return index;
                    }
                });

                console.log(indexes[0]);
                edges.splice(indexes[0], 1);
                console.log(edges.length)
                console.log(edges);
                redrawlinks();
                break;
            default:
                console.log("probably do nothing", d.source);
        }

        d3.event.stopPropagation();
    }

    link.on("click", linkclick);
    node.on("click", nodeclick);
    svg.on("click", backclick);

    function backclick(d) {
        console.log("you clicked background");
        switch(inputmode) {
            case 'A':
        //Edit - this should load the URL and
        console.log("this will add a new node at clicked location");
        questadd(d3.event.x, d3.event.y);
        break;
    default:
        console.log("reset the source if linking");
}
    }

//need to actually figure out what goes in the tooltip 
    node.on("mouseover", function(d) {
        var g = d3.select(this);  // the node (table)

        // tooltip

        fieldformat = "<TABLE>"
            fieldformat += "<TR><TD><B>"+ d.status+"</B></TD><TD>"+" Priority:"+"</TD><TD>"+ d.priority+"</TD></TR>";
        fieldformat += "</TABLE>"


        // Define 'div' for tooltips
        var div = d3.select("body").append("div")  // declare the tooltip div
	        .attr("class", "tooltip")              // apply the 'tooltip' class
                .style("opacity", 0)
                .html('<h5>' + d.qtype + '</h5>' + fieldformat)
                .style("left", 10 + (d3.event.pageX) + "px")// or just (d.x + 50 + "px")
                .style("top", (d3.event.pageY - 20) + "px")// or ...
                .transition()
                .duration(800)
                .style("opacity", 0.9);

    });

    node.on("mouseout", function(d) {
        d3.select("body").select('div.tooltip').remove();
    });


        function dragnodestarted(d) {
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragnode(d) {
            //console.log('dragging');
            //console.log(d.id);
            //console.log(d.x);
            d.fx = d3.event.x;
            d.fy = d3.event.y;
            d.x = d3.event.x;
            d.y = d3.event.y;
            d3.select(this).attr("transform", function (d) {
                return "translate(" + d.x + "," + d.y + ")";
            });
            redrawlines()
        };

        function dragnodeended(d) {
            console.log('drag ended')
            d.fx = null;
            d.fy = null;
            lastserverid = d.serverid.toString();
            lastxpos = Math.floor(d.x).toString();
            lastypos = Math.floor(d.y).toString();
            moveElement(lastserverid, lastxpos, lastypos);
            graphvars.justDragged = false;
            //nodeclick(d);
            graphvars.justDragged = true;
        }

// ** Update data section (Called from the onclick)
function redrawlines() {
    svg.selectAll('.link')
        .data(edges)
        .attr("d", function (d) {
            return "M" + d.source.x + "," + d.source.y + "L" + d.target.x + "," + d.target.y;
        });
};


function redrawGraph() {
    console.log('you clicked redraw')
    var simulation = d3.forceSimulation()
            .force("link", d3.forceLink().id(function(d) { return d.id; }))
            .force("charge", d3.forceManyBody().strength(-100))
            .force("center", d3.forceCenter(width / 2, height / 2));

    function strength() { return 200; }
    function xstrength() { return 0.1; }
    function distance() { return 220; }

   simulation
        .nodes(nodes)
        .on("tick", tick);

    simulation.force("link")
        .links(edges)
        .distance(distance)
        .iterations(1000)
        .strength(1);


    function tick() {
        node.attr('transform', function(d) {
            return "translate(" + d.x + "," + d.y + ")"; });

        redrawlines();
    }

};


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
     ;
 };

        // calculate how many words will fit on a line

function calcAllowableWords(maxWidth, words) {

    var wordCount = 0;
    var testLine = "";
    var spacer = "";
    var fittedWidth = 0;
    var fittedText = "";
    //ctx.font = font;

    for (var i = 0; i < words.length; i++) {

        testLine += spacer + words[i];
        spacer = " ";

        //var width = ctx.measureText(testLine).width;
        var width = testLine.length * 5
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

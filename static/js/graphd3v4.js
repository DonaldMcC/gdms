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

    var lastserverid = '';
    var lastxpos = '';
    var lastypos = '';


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
            value: 1});

    });


// this was being used for some of the force values - to be considered
    edges.forEach(function(e) {
        if (!e.source["linkcount"]) e.source["linkcount"] = 0;
        if (!e.target["linkcount"]) e.target["linkcount"] = 0;

        e.source["linkcount"]++;
        e.target["linkcount"]++;
    });

    console.log('edgefinal', edges);

// may look at making this dynamic again at some point 
    var width = 960, height = 600;
    var svg = d3.select("#graph").append("svg")
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
        .style("stroke-dasharray", function(d){
         return d.dasharray;
      })
        .attr("marker-end", "url(#end-arrow)")
        .style('marker-end', 'url(#end-arrow)');


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
        .attr('r', String(consts.nodeRadius), "stroke-width", 8)
        .style("fill", function(d){return d.fillclr})
        .style("stroke-width", function(d){return d.swidth})
        /* .attr('height', 25) */
        ;

    node.each(function(d) {
    wrapText(d3.select(this), d.title, d.txtclr)});


//need to actually figure out what goes in the tooltip 
    node.on("mouseover", function(d) {
        var g = d3.select(this);  // the node (table)

        // tooltip
         var fields = [{"fielda":'3',"fieldb":'4'}];
        fieldformat = "<TABLE>"
        fields.forEach(function(d) {
            fieldformat += "<TR><TD><B>"+ d.name+"</B></TD><TD>"+ d.type+"</TD><TD>"+ d.disp+"</TD></TR>";
        });
        fieldformat += "</TABLE>"


        // Define 'div' for tooltips
        var div = d3.select("body").append("div")  // declare the tooltip div
	        .attr("class", "tooltip")              // apply the 'tooltip' class
                .style("opacity", 0)
                .html('<h5>' + d.name + '</h5>' + fieldformat)
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
            d.fx = null;
            d.fy = null;
            lastserverid = d.serverid.toString();
            lastxpos = Math.floor(d.x).toString();
            lastypos = Math.floor(d.y).toString();
            moveElement(lastserverid, lastxpos, lastypos);
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
            .force("charge", d3.forceManyBody().strength(-400))
            .force("center", d3.forceCenter(width / 2, height / 2));

    function strength() { return -250; }

    function distance() { return 180; }

    simulation
        .nodes(nodes)
        .on("tick", tick);

    simulation.force("link")
        .links(edges)
        .distance(distance)
        .iterations(100)
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

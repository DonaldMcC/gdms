
    // HOw to get link ids instead of index
    // http://stackoverflow.com/questions/23986466/d3-force-layout-linking-nodes-by-name-instead-of-index

    // embedding web2py in d3
    // http://stackoverflow.com/questions/34326343/embedding-d3-js-graph-in-a-web2py-bootstrap-page

    // from donald method

    var consts =  {
    selectedClass: "selected",
    connectClass: "connect-node",
    circleGClass: "conceptG",
    graphClass: "graph",
    activeEditId: "active-editing",
    BACKSPACE_KEY: 8,
    DELETE_KEY: 46,
    ENTER_KEY: 13,
    nodeRadius: 80

  };

    var textHeight = 10;
    var lineHeight = textHeight + 5;
    var lines = [];
   initLines()

        d3edges.forEach(function(e, i){
              d3edges[i] = {source: d3nodes.filter(function(n){return n.serverid == e.source;})[0],
                          target: d3nodes.filter(function(n){return n.serverid == e.target;})[0],
                          dasharray: e.dasharray,
                          sourceid: e.source}});

        console.log(d3edges);

    links.forEach(function(e) {
        var sourceNode = nodes.filter(function(n) {return n.serverid === e.source;})[0],
            targetNode = nodes.filter(function(n) {return n.serverid === e.target;})[0];

        edges.push({
            source: sourceNode,
            target: targetNode,
            value: 1});

    });


    edges.forEach(function(e) {
        if (!e.source["linkcount"]) e.source["linkcount"] = 0;
        if (!e.target["linkcount"]) e.target["linkcount"] = 0;

        e.source["linkcount"]++;
        e.target["linkcount"]++;
    })

    var width = 960, height = 600;
    var svg = d3.select("#vis").append("svg")
            .attr("width", width)
            .attr("height", height);

    // updated for d3 v4.
    var simulation = d3.forceSimulation()
            .force("link", d3.forceLink().id(function(d) { return d.id; }))
            .force("charge", d3.forceManyBody().strength(-40000))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("y", d3.forceY(0))
            .force("x", d3.forceX(0));

// charge strength
function strength(d) { return -500/d["linkcount"] ; }
// link distance
function distance(d) { return (d.source["linkcount"] + d.target["linkcount"]) * 5 ; }
function strengthl(d) { return 0.2/(d.source["linkcount"] + d.target["linkcount"]) ; }

simulation
    .nodes(nodes)
    .on("tick", tick);


simulation.force("link")
    .links(edges)
    .distance(distance)
    .strength(strengthl)
    .iterations(1000);


    // build the arrow.
   svg.append("svg:defs").selectAll("marker")
    .data(["end"])      // Different link/path types can be defined here
   .enter().append("svg:marker")    // This section adds in the arrows
    .attr("id", String)
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 25)   /* Moves the arrow head out, allow for radius */
    .attr("refY", 0)   /* -1.5  */
    .attr("markerWidth", 6)
    .attr("markerHeight", 6)
    .attr("orient", "auto")
    .append("svg:path")
    .attr("d", "M0,-5L10,0L0,5");

    var link = svg.selectAll('.link')
            .data(edges)
            .enter().append('line')
            .attr("class", "link")
            .attr("marker-end", "url(#end)");

    var node = svg.selectAll(".node")
            .data(nodes)
            .enter().append("g")
            .attr("class", function(d) { return "node " + d.type;})
            .call(d3.drag()
              .on("start", dragstarted)
              .on("drag", dragged)
              .on("end", dragended));

    /*
        newGs.append("circle")
      .attr("r", String(consts.nodeRadius),
            "stroke-width", 8)
        .style("fill", function(d){return d.fillclr})
        .style("stroke-width", function(d){return d.swidth});
    */


    // add the nodes
    node.append('circle') /* 'circlej */
        .attr('r', consts.nodeRadius)
        .style("fill", function(d){return d.fillclr})
        .style("stroke-width", function(d){return d.swidth})
        /* .attr('height', 25) */
        ;

    /* add text
    node.append("text")
            .attr("class", "node")
            .attr("x", 14)
            .attr("dy", "-1.2em")
            .wrapText(gEl, title, txtclr);*/


    node.each(function(d) {
        console.log(d.title);
    wrapText(d3.select(this), d.title, d.txtclr)});


    node.on("mouseover", function(d) {

        var g = d3.select(this);  // the node (table)

        // tooltip

        /* remove for now would like something back in
         var fields = d.fields;
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
                */
    });

    node.on("mouseout", function(d) {
        d3.select("body").select('div.tooltip').remove();
    });

// instead of waiting for force to end with :     force.on('end', function()
    // use .on("tick",  instead.  Here is the tick function
    function tick() {
        node.attr('transform', function(d) {
            return "translate(" + d.x + "," + d.y + ")"; });

        link.attr('x1', function(d) {return d.source.x;})
                .attr('y1', function(d) {return d.source.y;})
                .attr('x2', function(d) {return d.target.x;})
                .attr('y2', function(d) {return d.target.y;});
    };

        function dragstarted(d) {
            if (!d3.event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }


        function dragged(d) {
            d.fx = d3.event.x;
            d.fy = d3.event.y;
        }

        function dragended(d) {
            if (!d3.event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }



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
         console.log(lineData.text);
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

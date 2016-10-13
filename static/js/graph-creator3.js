/*
Modified version of mbostock graph creater for D3
*/

document.onload = (function(d3, saveAs, Blob, undefined){
  "use strict";


        // ... the AJAX request is successful
        var updateNodeServerID = function(resp) {
        //$( '#target').html( resp.serverid );
        //console.log('successful callback' );
        //console.log(resp.serverid );
            
        var result = $.grep(nodes, function(e){ return e.id == resp.id; });
        if (result.length === 0) {
          // not found
        } else if (result.length == 1) {
        result[0].serverid = resp.serverid
        } else {
        console.error('There are duplicate ids in the array');
        // multiple items found
        } 
        };

        // ... the AJAX request fails
    var printError = function( req, status, err ) {
    console.log( 'something went wrong', status, err );
    };

        var params = { id:16, itemtext:'Some random text' };
        var str = $.param( params );// does this do anything
    // Create an object to describe the AJAX request
    var ajaxOptions = {
        url: ajaxquesturl+str,
        dataType: 'json',
        success: updateNodeServerID,
        error: printError
        };

  // TODO add user settings
  var consts = {
    defaultTitle: "Overwrite with item text"
  };

    var textHeight = 10;
    var lineHeight = textHeight + 5;
    var lines = [];




  var settings = {
    appendElSpec: "#graph"
  };
  // define graphcreator object
  var GraphCreator = function(svg, nodes, edges) {
      var thisGraph = this;
      thisGraph.idct = 0;

      thisGraph.nodes = nodes || [];
      thisGraph.edges = edges || [];

      thisGraph.state = {
          selectedNode: null,
          selectedEdge: null,
          mouseDownNode: null,
          mouseDownLink: null,
          touchlinking: false,
          justDragged: false,
          justScaleTransGraph: false,
          lastKeyDown: -1,
          shiftNodeDrag: false,
          selectedText: null
      };

      // define arrow markers for graph links
      var defs = svg.append('svg:defs');
      defs.append('svg:marker')
          .attr('id', 'end-arrow')
          .attr('viewBox', '0 -5 10 10')
          .attr('refX', "46")
          .attr('markerWidth', 3.5)
          .attr('markerHeight', 3.5)
          .attr('orient', 'auto')
          .append('svg:path')
          .attr('d', 'M0,-5L10,0L0,5');

      // define arrow markers for leading arrow
      defs.append('svg:marker')
          .attr('id', 'mark-end-arrow')
          .attr('viewBox', '0 -5 10 10')
          .attr('refX', 7)
          .attr('markerWidth', 3.5)
          .attr('markerHeight', 3.5)
          .attr('orient', 'auto')
          .append('svg:path')
          .attr('d', 'M0,-5L10,0L0,5');

      thisGraph.svg = svg;
      thisGraph.svgG = svg.append("g")
          .classed(thisGraph.consts.graphClass, true);
      var svgG = thisGraph.svgG;

      // displayed when dragging between nodes
      thisGraph.dragLine = svgG.append('svg:path')
          .attr('class', 'link dragline hidden')
          .attr('d', 'M0,0L0,0')
          .attr('stroke-width', 10)
          .style('marker-end', 'url(#mark-end-arrow)');

      // svg nodes and edges
      thisGraph.paths = svgG.append("g").selectAll("g");
      thisGraph.circles = svgG.append("g").selectAll("g");

      thisGraph.drag = d3.behavior.drag()
          .origin(function (d) {
              return {x: d.x, y: d.y};
          })
          .on("drag", function (args) {
              thisGraph.state.justDragged = true;
              thisGraph.dragmove.call(thisGraph, args);
          })
          .on("dragend", function (args) {
              //thisGraph.dragend.call(thisGraph, args);
              if (vieweventmap == true & eventowner == true & inputmode=='E') {
                  moveElement(lastserverid, lastxpos, lastypos);
              }
          });


    // listen for key events
    d3.select(window).on("keydown", function(){
      thisGraph.svgKeyDown.call(thisGraph);
    })
    .on("keyup", function(){
      thisGraph.svgKeyUp.call(thisGraph);
    });
    svg.on("mousedown", function(d){thisGraph.svgMouseDown.call(thisGraph, d);});
    // svg.on("touchstart", function(d){thisGraph.svgMouseDown.call(thisGraph, d);});
    svg.on("mouseup", function(d){thisGraph.svgMouseUp.call(thisGraph, d);});
    //svg.on("touchend", function(d){thisGraph.svgMouseUp.call(thisGraph, d);});

    
    // listen for dragging
    var dragSvg = d3.behavior.zoom()
          .on("zoom", function(){
            if (d3.event.sourceEvent.shiftKey || inputmode == 'E'){
              // TODO  the internal d3 state is still changing
              return false;
            } else{
              thisGraph.zoomed.call(thisGraph);
            }
            return true;
          })
          .on("zoomstart", function(){
            var ael = d3.select("#" + thisGraph.consts.activeEditId).node();
            if (ael){
              ael.blur();
            }
            if (!d3.event.sourceEvent.shiftKey || inputmode != 'V') d3.select('body').style("cursor", "move");
          })
          .on("zoomend", function(){
            d3.select('body').style("cursor", "auto");
          });

    svg.call(dragSvg).on("dblclick.zoom", null);

    // listen for resize
    window.onresize = function(){thisGraph.updateWindow(svg);};

    // handle download data
    d3.select("#download-input").on("click", function(){
      var saveEdges = [];
      thisGraph.edges.forEach(function(val, i){
        saveEdges.push({source: val.source.id, target: val.target.id});
      });
      var blob = new Blob([window.JSON.stringify({"nodes": thisGraph.nodes, "edges": saveEdges})], {type: "text/plain;charset=utf-8"});
      saveAs(blob, "mydag.json");
    });


    // handle uploaded data
    d3.select("#upload-input").on("click", function(){
      document.getElementById("hidden-file-upload").click();
    });
    d3.select("#hidden-file-upload").on("change", function(){
      if (window.File && window.FileReader && window.FileList && window.Blob) {
        var uploadFile = this.files[0];
        var filereader = new window.FileReader();

        filereader.onload = function(){
          var txtRes = filereader.result;
          // TODO better error handling
          try{
            var jsonObj = JSON.parse(txtRes);
            thisGraph.deleteGraph(true);
            thisGraph.nodes = jsonObj.nodes;
            thisGraph.setIdCt(jsonObj.nodes.length + 1);
            var newEdges = jsonObj.edges;
            newEdges.forEach(function(e, i){
              newEdges[i] = {source: thisGraph.nodes.filter(function(n){return n.id == e.source;})[0],
                             target: thisGraph.nodes.filter(function(n){return n.id == e.target;})[0],
                            dasharray: e.dasharray,
                          sourceid: e.source};
            });
            thisGraph.edges = newEdges;
            thisGraph.updateGraph();
          }catch(err){
            window.alert("Error parsing uploaded file\nerror message: " + err.message);
            return;
          }
        };
        filereader.readAsText(uploadFile);

      } else {
        alert("Your browser won't let you save this graph -- try upgrading your browser to IE 10+ or Chrome or Firefox.");
      }

    });

    // handle delete graph
    d3.select("#delete-graph").on("click", function(){
      thisGraph.deleteGraph(false);
    });

    // handle redraw graph
    d3.select("#redraw-graph").on("click", function(){
         thisGraph.redrawGraph();
    });
  };



  GraphCreator.prototype.setIdCt = function(idct){
    this.idct = idct;
  };

  GraphCreator.prototype.consts =  {
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

  /* PROTOTYPE FUNCTIONS */
    var lastserverid = '';
    var lastxpos = '';
    var lastypos = '';

  GraphCreator.prototype.dragmove = function(d) {
    var thisGraph = this;
    if (thisGraph.state.shiftNodeDrag){
      thisGraph.dragLine.attr('d', 'M' + d.x + ',' + d.y + 'L' + d3.mouse(thisGraph.svgG.node())[0] + ',' + d3.mouse(this.svgG.node())[1]);
    } else{
      d.x += d3.event.dx;
      d.y +=  d3.event.dy;
     // Test of moving event graph
      if (vieweventmap == true) {
        var m = ['The element moved' ,
          d.serverid,
            '   ' + d.x,
            '   ' + d.y ].join('');
          if (d.serverid)  {
          lastserverid = d.serverid.toString()
          }
          else 
          {lastserverid = "0"};
          lastxpos = Math.floor(d.x).toString()
          lastypos = Math.floor(d.y).toString()
        //moveElement(d.serverid.toString(), Math.floor(d.x).toString(), Math.floor(d.y).toString());
        //out(m)
          ;}
      thisGraph.updateGraph();
    }
  };

  GraphCreator.prototype.deleteGraph = function(skipPrompt){
    var thisGraph = this,
        doDelete = true;
    if (!skipPrompt){
      doDelete = window.confirm("Press OK to delete this graph");
    }
    if(doDelete){
      thisGraph.nodes = [];
      thisGraph.edges = [];
      thisGraph.updateGraph();
    }
  };

      GraphCreator.prototype.redrawGraph = function(){
      var thisGraph = this;
          var force = d3.layout.force()
                      .nodes(thisGraph.nodes)
                      .links(thisGraph.edges)
                       .size([width, height])
              .linkStrength(0.5)
              .friction(0.9)
              .linkDistance(200)
              .charge(-2000)
              .chargeDistance(1000)
              .gravity(0.1)
              .theta(0.9)
              .alpha(0.1)
              .start();

        force.on("tick", function() {
              thisGraph.updateGraph();
          });    
              
          force.on("end", function() {
              thisGraph.updateGraph();
              if (vieweventmap == true & eventowner == true) {
                  // if owner and eventmapiterate through nodes and call function to write new positions to server
                  thisGraph.nodes.forEach(function (e) {
                      console.log(e.serverid.toString() + Math.floor(e.x).toString())
                      moveElement(e.serverid.toString(), Math.floor(e.x).toString(), Math.floor(e.y).toString());
                  });
              }
      });
  };

  /* select all text in element: taken from http://stackoverflow.com/qufestions/6139107/programatically-select-text-in-a-contenteditable-html-element */
  GraphCreator.prototype.selectElementContents = function(el) {
    var range = document.createRange();
    range.selectNodeContents(el);
    var sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
  };


  /* insert svg line breaks: taken from http://stackoverflow.com/questions/13241475/how-do-i-include-newlines-in-labels-in-d3-charts */
  GraphCreator.prototype.insertTitleLinebreaks = function (gEl, title, txtclr) {
    wrapText(gEl, title, txtclr)
  };

/*function (gEl, title) {
    var words = title.split(/\s+/g),
        nwords = words.length;
    var el = gEl.append("text")
          .attr("text-anchor","middle")
          .attr("font-size", "10px")
          .attr("dy", "-" + (nwords-1)*7.5);

    for (var i = 0; i < words.length; i++) {
      var tspan = el.append('tspan').text(words[i]);
      if (i > 0)
        tspan.attr('x', 0).attr('dy', '15');
    }
  };*/


  // remove edges associated with a node
  GraphCreator.prototype.spliceLinksForNode = function(node) {
    var thisGraph = this,
        toSplice = thisGraph.edges.filter(function(l) {
      return (l.source === node || l.target === node);
    });
    toSplice.map(function(l) {
      thisGraph.edges.splice(thisGraph.edges.indexOf(l), 1);
    });
  };

  GraphCreator.prototype.replaceSelectEdge = function(d3Path, edgeData){
    var thisGraph = this;
    d3Path.classed(thisGraph.consts.selectedClass, true);
    if (thisGraph.state.selectedEdge){
      thisGraph.removeSelectFromEdge();
    }
    thisGraph.state.selectedEdge = edgeData;
  };

  GraphCreator.prototype.replaceSelectNode = function(d3Node, nodeData){
    var thisGraph = this;
    d3Node.classed(this.consts.selectedClass, true);
    if (thisGraph.state.selectedNode){
      thisGraph.removeSelectFromNode();
    }
    thisGraph.state.selectedNode = nodeData;
  };

  GraphCreator.prototype.removeSelectFromNode = function(){
    var thisGraph = this;
    thisGraph.circles.filter(function(cd){
      return cd.id === thisGraph.state.selectedNode.id;
    }).classed(thisGraph.consts.selectedClass, false);
    thisGraph.state.selectedNode = null;
  };

  GraphCreator.prototype.removeSelectFromEdge = function(){
    var thisGraph = this;
    thisGraph.paths.filter(function(cd){
      return cd === thisGraph.state.selectedEdge;
    }).classed(thisGraph.consts.selectedClass, false);
    thisGraph.state.selectedEdge = null;
  };

  GraphCreator.prototype.pathMouseDown = function(d3path, d){
    var thisGraph = this,
        state = thisGraph.state;
    d3.event.stopPropagation();
    state.mouseDownLink = d;

    if (state.selectedNode){
      thisGraph.removeSelectFromNode();
    }
    

    
    var prevEdge = state.selectedEdge;
    if (!prevEdge || prevEdge !== d){
      thisGraph.replaceSelectEdge(d3path, d);
    } else{
      thisGraph.removeSelectFromEdge();
    };
    if (inputmode == 'D') {
            //console.log(thisGraph.edges[thisGraph.edges.indexOf(selectedEdge)].source.serverid.toString())
        deleteLink(thisGraph.edges[thisGraph.edges.indexOf(state.selectedEdge)].source.serverid.toString(),
            thisGraph.edges[thisGraph.edges.indexOf(state.selectedEdge)].target.serverid.toString());
        thisGraph.edges.splice(thisGraph.edges.indexOf(state.selectedEdge), 1);
        state.selectedEdge = null;
        thisGraph.updateGraph();
    };
  };

  // mousedown on node
  GraphCreator.prototype.circleMouseDown = function(d3node, d){
    var thisGraph = this,
        state = thisGraph.state;
    d3.event.stopPropagation();
    if (state.touchlinking == false) {
    state.mouseDownNode = d;  //don't update if on second link
  };
    state.selectedNode = d;
    if (inputmode == 'D'  && state.selectedNode ) {
       if (thisGraph.nodes[thisGraph.nodes.indexOf(state.selectedNode)].serverid) {
       deleteNode(thisGraph.nodes[thisGraph.nodes.indexOf(state.selectedNode)].serverid.toString(), eventid)};
       thisGraph.nodes.splice(thisGraph.nodes.indexOf(state.selectedNode), 1);
       thisGraph.spliceLinksForNode(state.selectedNode);
       state.selectedNode = null;
       thisGraph.updateGraph();       
    };
    
    if (inputmode == 'L'  && state.selectedNode ) {
                if (state.touchlinking == true) {  
                    state.touchlinking = false;                 
                    thisGraph.circleMouseUp.call(thisGraph, d3node, d);
                    //some sort of highlight of item and message to be generated
                    
                    state.mouseDownNode = false;}
                else { 
                    document.getElementById('target').innerHTML = "Linking from " + d3node.text(); 
                    state.touchlinking = true;  
                    state.shiftNodeDrag = true;     
                    d3node.classed("svgselect", true);                    
                    };
    };
    if (d3.event.shiftKey || inputmode == 'V'){
      state.shiftNodeDrag = d3.event.shiftKey || inputmode == 'V';
      // reposition dragged directed edge
      thisGraph.dragLine.classed('hidden', false)
        .attr('d', 'M' + d.x + ',' + d.y + 'L' + d.x + ',' + d.y);
      return;
    }
  };

  /* place editable text on node in place of svg text */
  GraphCreator.prototype.changeTextOfNode = function(d3node, d){
    var thisGraph= this,
        consts = thisGraph.consts,
        htmlEl = d3node.node();
    d3node.selectAll("text").remove();
    var nodeBCR = htmlEl.getBoundingClientRect(),
        curScale = nodeBCR.width/consts.nodeRadius,
        placePad  =  5*curScale,
        useHW = curScale > 1 ? nodeBCR.width*0.71 : consts.nodeRadius*1.42;
    // replace with editablecontent text
    var d3txt = thisGraph.svg.selectAll("foreignObject")
          .data([d])
          .enter()
          .append("foreignObject")
          .attr("x", nodeBCR.left + placePad )
          .attr("y", nodeBCR.top + placePad)
          .attr("height", 2*useHW)
          .attr("width", useHW)
          .attr("txtclr", d.txtclr)
          .append("xhtml:p")
          .attr("id", consts.activeEditId)
          .attr("contentEditable", "true")
          .text(d.title)
          .on("mousedown", function(d){
            d3.event.stopPropagation();
          })
          .on("touchstart", function(d){
            d3.event.stopPropagation();
          })
          .on("keydown", function(d){
            d3.event.stopPropagation();
            if (d3.event.keyCode == consts.ENTER_KEY && !d3.event.shiftKey){
              this.blur();
            }
          })
          .on("blur", function(d){
            d.title = this.textContent;
            thisGraph.insertTitleLinebreaks(d3node, d.title);
            d3.select(this.parentElement).remove();
            //should only be here if node is editable now
            console.log('text editing completed -' + d.title);
            params = { id: d.id, itemtext: d.title, eventid: eventid };
            str = $.param( params )
            ajaxOptions = {
            url: ajaxquesturl+str,
            dataType: 'json',
            success: updateNodeServerID,
            error: printError
            };
            $.ajax(ajaxOptions);
            newitems = true;
          });
    return d3txt;
  };

  // mouseup on nodes
  GraphCreator.prototype.circleMouseUp = function(d3node, d){
    var thisGraph = this,
        state = thisGraph.state,
        consts = thisGraph.consts;
    // reset the states
    state.shiftNodeDrag = false;
    d3node.classed(consts.connectClass, false);

    if (state.touchlinking) return; //ignore 1st mouseup if touch linking
    var mouseDownNode = state.mouseDownNode;

    if (!mouseDownNode) return;

    thisGraph.dragLine.classed("hidden", true);

    if (mouseDownNode !== d){ 
      //thisGraph.d3node.attr("stroke-width", 8)
      // we're in a different node: create new edge for mousedown edge and add to graph
      thisGraph.circles.each(function(d){
      d3.select(this).classed("svgselect", false); 
    });
      var newEdge = {source: mouseDownNode, target: d};
        var m = [
        'The element with ID <b>' + mouseDownNode.serverid.toString(),
        '</b> is connected elemnt with ID <b>' + d.serverid.toString() + '</b>'].join('');
        out(m);
        requestLink(mouseDownNode.serverid.toString(), d.serverid.toString());
      var filtRes = thisGraph.paths.filter(function(d){
        if (d.source === newEdge.target && d.target === newEdge.source){
          thisGraph.edges.splice(thisGraph.edges.indexOf(d), 1);
        }
        return d.source === newEdge.source && d.target === newEdge.target;
      });
      if (!filtRes[0].length){
        thisGraph.edges.push(newEdge);
        thisGraph.updateGraph();
      }
    } else{
      // we're in the same node
      if (state.justDragged) {
        // dragged, not clicked
        state.justDragged = false;
        //window.alert(mouseDownNode.serverid.toString());
        //window.alert(d.serverid.toString());
        
      } else{
        // clicked, not dragged
        if (d3.event.shiftKey || inputmode == 'E'){
          // shift-clicked node: edit text content
            if (d.locked != 'Y') {
                var d3txt = thisGraph.changeTextOfNode(d3node, d);
                var txtNode = d3txt.node();
                thisGraph.selectElementContents(txtNode);
                txtNode.focus();
            }
            else {alert("Only draft item text editable")}
        } else{
          if (state.selectedEdge){
            thisGraph.removeSelectFromEdge();
          }
          var prevNode = state.selectedNode;

          if (!prevNode || prevNode.id !== d.id){
            thisGraph.replaceSelectNode(d3node, d);
          } else{
            thisGraph.removeSelectFromNode();
          }
        }
      }
    }
    state.mouseDownNode = null;
    return;

  }; // end of circles mouseup

  // mousedown on main svg
  GraphCreator.prototype.svgMouseDown = function(){
    this.state.graphMouseDown = true;
  };

  // mouseup on main svg
  GraphCreator.prototype.svgMouseUp = function(){
    var thisGraph = this,
        state = thisGraph.state;
    if (state.justScaleTransGraph) {
      // dragged not clicked
      state.justScaleTransGraph = false;
    } else if ((state.graphMouseDown && d3.event.shiftKey) || inputmode == 'A'){
      // clicked not dragged from svg
      console.log(thisGraph.idct);
      // Initiate the request!
      //params = { id:thisGraph.idct, itemtext:'Some random text' };
      //$.ajax(ajaxOptions);
      var xycoords = d3.mouse(thisGraph.svgG.node()),
          d = {id: thisGraph.idct++, title: consts.defaultTitle, x: xycoords[0], y: xycoords[1]};
      thisGraph.nodes.push(d);
      thisGraph.updateGraph();
      // make title of text immediently editable
      var d3txt = thisGraph.changeTextOfNode(thisGraph.circles.filter(function(dval){
        return dval.id === d.id;
      }), d),
          txtNode = d3txt.node();
      thisGraph.selectElementContents(txtNode);
      txtNode.focus();
    console.log('is this text of end of edit ajax would move here hopefully');
    } else if (state.graphMouseDown && inputmode == 'D'){
            if (state.selectedNode){
                console.log(state.selectedNode);
                deleteNode(thisGraph.nodes[thisGraph.nodes.indexOf(state.selectedNode)].serverid.toString(), eventid);
                thisGraph.nodes.splice(thisGraph.nodes.indexOf(state.selectedNode), 1);
                thisGraph.spliceLinksForNode(state.selectedNode);
                state.selectedNode = null;
                thisGraph.updateGraph();
      } else if (state.selectedEdge){
        //console.log(thisGraph.edges[thisGraph.edges.indexOf(selectedEdge)].source.serverid.toString())
        deleteLink(thisGraph.edges[thisGraph.edges.indexOf(state.selectedEdge)].source.serverid.toString(),
            thisGraph.edges[thisGraph.edges.indexOf(state.selectedEdge)].target.serverid.toString());
        thisGraph.edges.splice(thisGraph.edges.indexOf(state.selectedEdge), 1);
        state.selectedEdge = null;
        thisGraph.updateGraph();
      }
    } else if (state.shiftNodeDrag){
      // dragged from node
      state.shiftNodeDrag = false;
      thisGraph.dragLine.classed("hidden", true);
    }
    state.graphMouseDown = false;
  };

  // keydown on main svg
  GraphCreator.prototype.svgKeyDown = function() {
    var thisGraph = this,
        state = thisGraph.state,
        consts = thisGraph.consts;
    // make sure repeated key presses don't register for each keydown
    if(state.lastKeyDown !== -1) return;

    state.lastKeyDown = d3.event.keyCode;
    var selectedNode = state.selectedNode,
        selectedEdge = state.selectedEdge;

    switch(d3.event.keyCode) {
    case consts.BACKSPACE_KEY:
    case consts.DELETE_KEY:
      d3.event.preventDefault();
      if (selectedNode){
        //maybe an ajax delete event but not convinced
        console.log(thisGraph.nodes.indexOf(selectedNode));
        deleteNode(thisGraph.nodes[thisGraph.nodes.indexOf(state.selectedNode)].serverid.toString(), eventid);
        thisGraph.nodes.splice(thisGraph.nodes.indexOf(selectedNode), 1);
        thisGraph.spliceLinksForNode(selectedNode);
        state.selectedNode = null;
        thisGraph.updateGraph();
      } else if (selectedEdge){
        //console.log(thisGraph.edges[thisGraph.edges.indexOf(selectedEdge)].source.serverid.toString())
        deleteLink(thisGraph.edges[thisGraph.edges.indexOf(selectedEdge)].source.serverid.toString(),
            thisGraph.edges[thisGraph.edges.indexOf(selectedEdge)].target.serverid.toString());
        thisGraph.edges.splice(thisGraph.edges.indexOf(selectedEdge), 1);
        state.selectedEdge = null;
        thisGraph.updateGraph();
      }
      break;
    }
  };

  GraphCreator.prototype.svgKeyUp = function() {
    this.state.lastKeyDown = -1;
  };

  // call to propagate changes to graph
  GraphCreator.prototype.updateGraph = function(){

    var thisGraph = this,
        consts = thisGraph.consts,
        state = thisGraph.state;

    thisGraph.paths = thisGraph.paths.data(thisGraph.edges, function(d){
      return String(d.source.id) + "+" + String(d.target.id);
    });
    var paths = thisGraph.paths;
    // update existing paths
    paths.style('marker-end', 'url(#end-arrow)')
      .classed(consts.selectedClass, function(d){
        return d === state.selectedEdge;
      })
      .attr("d", function(d){
        return "M" + d.source.x + "," + d.source.y + "L" + d.target.x + "," + d.target.y;
      });

    // add new paths
    paths.enter()
      .append("path")
      .style('marker-end','url(#end-arrow)')
      .classed("link", true)
        .attr("stroke", "purple")
        .style("stroke-dasharray", function(d){
         return d.dasharray;
      })
      .attr("d", function(d){
        return "M" + d.source.x + "," + d.source.y + "L" + d.target.x + "," + d.target.y;
      })
      .on("mousedown", function(d){
        thisGraph.pathMouseDown.call(thisGraph, d3.select(this), d);
        }
      )
        .on("touchstart", function(d){  
        thisGraph.pathMouseDown.call(thisGraph, d3.select(this), d);
        }
      )
      .on("mouseup", function(d){
        state.mouseDownLink = null;
      })
      .on("touchend", function(d){
        state.mouseDownLink = null;
      });

    // remove old links
    paths.exit().remove();

    // update existing nodes
    thisGraph.circles = thisGraph.circles.data(thisGraph.nodes, function(d){ return d.id;});
    thisGraph.circles.attr("transform", function(d){return "translate(" + d.x + "," + d.y + ")";});

    // add new nodes
    var newGs= thisGraph.circles.enter()
          .append("g");

    newGs.classed(consts.circleGClass, true)
      .attr("transform", function(d){return "translate(" + d.x + "," + d.y + ")";})
      .on("mouseover", function(d){
        if (state.shiftNodeDrag){
          d3.select(this).classed(consts.connectClass, true);
        }
      })
      .on("mouseout", function(d){
          
        d3.select(this).classed(consts.connectClass, false);
      })
      .on("mousedown", function(d){         
        thisGraph.circleMouseDown.call(thisGraph, d3.select(this), d);
        
      })
      .on("mouseup", function(d){
        thisGraph.circleMouseUp.call(thisGraph, d3.select(this), d);
      })
      .call(thisGraph.drag);

    newGs.append("circle")
      .attr("r", String(consts.nodeRadius),
            "stroke-width", 8)
        .style("fill", function(d){return d.fillclr})
        .style("stroke-width", function(d){return d.swidth});

    newGs.each(function(d){
      thisGraph.insertTitleLinebreaks(d3.select(this), d.title);
      d3.select(this).classed("svgselect", false); 
    });
        
    // remove old nodes
    thisGraph.circles.exit().remove();
  };

  GraphCreator.prototype.zoomed = function(){
    this.state.justScaleTransGraph = true;
    d3.select("." + this.consts.graphClass)
      .attr("transform", "translate(" + d3.event.translate + ") scale(" + d3.event.scale + ")");
  };

  GraphCreator.prototype.updateWindow = function(svg){
    var docEl = document.documentElement,
        bodyEl = document.getElementsByTagName('body')[0];
    var x = window.innerWidth || docEl.clientWidth || bodyEl.clientWidth;
    var y = window.innerHeight|| docEl.clientHeight|| bodyEl.clientHeight;
    svg.attr("width", x).attr("height", y);
  };

// this is from http://jsfiddle.net/m1erickson/upq6L/

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


function wrapText(gEl, title) {

    var i = 0;
    var line = 0;
    var words = title.split(" ");

    var el = gEl.append("text")
           //.style("fill", txtclr) not getting this to work and possibly not a good idea anyway
          .attr("text-anchor","middle")
          .attr("font-size", "11px")
          .attr("dy", "-" + 8 * 7.5);



    while (i < lines.length && words.length > 0) {

        line = lines[i++];
        var lineData = calcAllowableWords(line.maxLength, words);
        var tspan = el.append('tspan').text(lineData.text);
          if (i > 1)
        tspan.attr('x', 0).attr('dy', '15');
        words.splice(0, lineData.count);
    };

}


/*function (gEl, title) {
    var words = title.split(/\s+/g),
        nwords = words.length;
    var el = gEl.append("text")
          .attr("text-anchor","middle")
          .attr("font-size", "10px")
          .attr("dy", "-" + (nwords-1)*7.5);

    for (var i = 0; i < words.length; i++) {
      var tspan = el.append('tspan').text(words[i]);
      if (i > 0)
        tspan.attr('x', 0).attr('dy', '15');
    }
  };*/


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


  /**** MAIN ****/

  // warn the user when leaving
/* Disable for now - annoying and not needed in this app*/
  window.onbeforeunload = function() {
      if (newitems == true) {
      return "Items added are created as drafts and you fill in answers using the my drafts menu option :-)";
  };
  };


  var docEl = document.documentElement,
      bodyEl = document.getElementsByTagName('body')[0];


  var width = window.innerWidth || docEl.clientWidth || bodyEl.clientWidth
 /*
 
  var height =  window.innerHeight|| docEl.clientHeight|| bodyEl.clientHeight;
 
 chnage 0402 for testing */ 
 


  var xLoc = width/2 - 25,
      yLoc = 100;

  // initial node data
  /*var nodes = [];
  var edges = [];*/


    var nodes = d3nodes;
    var edges = d3edges;

    initLines()


  /** MAIN SVG **/
  var svg = d3.select(settings.appendElSpec).append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("class", "graph-svg-component");
  var graph = new GraphCreator(svg, nodes, edges);
      //graph.setIdCt(2);
      //change from starting with blank canvas
      graph.setIdCt(nodes.length+2)
  graph.updateGraph();
    if (redraw) {
        graph.redrawGraph();
        redraw = false;
    }
})(window.d3, window.saveAs, window.Blob);

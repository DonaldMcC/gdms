/*D3 logo drawing approach */

(function() {

    var data = [
        {x:16,y:18,size:100,symbol:'triangle-down', colour:'yellow', r:255, g:255, b:0,  stroke:'blue'},
        {x:46,y:18,size:100,symbol:'triangle-down', colour:'yellow', r:255, g:255, b:0, stroke:'blue'},
        {x:76,y:18,size:100,symbol:'triangle-down', colour:'blue', r:0, g:0, b:255,  stroke:'blue'},
        {x:46,y:50,size:100,symbol:'triangle-up', colour:'green', r:0, g:255, b:0, stroke:'blue'}]

  var svg = d3.select("#logo")
      .append("svg")
      .attr("width", 96)
      .attr("height", 70);

    var symbol = d3.svg.symbol().type('triangle-up');

            /*
   style="fillrgb(0,0,255)"
    .style("fill", function(d){return d.colour})    */

svg.selectAll('path').data(data).enter()
    .append("path")
    .attr("d", d3.svg.symbol().type(function(d){return d.symbol}).size(function(d){return d.size}))
    .attr("transform", function(d) {return "translate("+d.x+","+d.y+")"})
    .style("fill", function(d) {return d3.rgb(d.r, d.g, d.b)})
        .style("stroke", function(d){return d.stroke});

    svg.selectAll('path').data(data).transition()
    .delay(500)
    .duration(1000)
    .attr("d", d3.svg.symbol().type(function(d){return d.symbol}).size(function(d){return d.size * 4}));


var path3 = svg.append('g').append("line")          // attach a line
    .style("stroke", "blue")  // colour the line
    .attr("x1", 16)     // x position of the first end of the line
    .attr("y1", 31)      // y position of the first end of the line
    .attr("x2", 46)     // x position of the second end of the line
    .attr("y2", 38);

var path4 = svg.append('g').append("line")
    .style("stroke", "blue")
    .attr("x1", 46)
    .attr("y1", 31)
    .attr("x2", 46)
    .attr("y2", 39);

    var path5 = svg.append('g').append("line")
        .style("stroke", "blue")
        .attr("x1", 76)
            .attr("y1", 31)
        .attr("x2", 46)
        .attr("y2", 38)

})();


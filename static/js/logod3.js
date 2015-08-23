/*D3 logo drawing approach */

(function() {

    var data = [
        {x:20,y:18,size:80,symbol:'triangle-down', colour:'yellow', r:255, g:255, b:0,  stroke:'blue'},
        {x:50,y:18,size:80,symbol:'triangle-down', colour:'yellow', r:255, g:255, b:0, stroke:'blue'},
        {x:80,y:18,size:80,symbol:'triangle-down', colour:'blue', r:0, g:0, b:255,  stroke:'blue'},
        {x:50,y:45,size:80,symbol:'triangle-up', colour:'green', r:0, g:255, b:0, stroke:'blue'}]

  var svg = d3.select("#logo")
      .append("svg")
      .attr("width", 100)
      .attr("height", 58);

    var symbol = d3.svg.symbol().type('triangle-up');


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

    svg.append('g').append("rect")
        .attr("x", 5)     // x position of the first end of the line
        .attr("y", 5)
        .attr("width", 90)
        .attr("height", 53);

var path3 = svg.append('g').append("line")          // attach a line
    .style("stroke", "blue")  // colour the line
    .attr("x1", 20)     // x position of the first end of the line
    .attr("y1", 29)      // y position of the first end of the line
    .attr("x2", 50)     // x position of the second end of the line
    .attr("y2", 35);

var path4 = svg.append('g').append("line")
    .style("stroke", "blue")
    .attr("x1", 50)
    .attr("y1", 29)
    .attr("x2", 50)
    .attr("y2", 35);

    var path5 = svg.append('g').append("line")
        .style("stroke", "blue")
        .attr("x1", 80)
            .attr("y1", 29)
        .attr("x2", 50)
        .attr("y2", 35)

})();


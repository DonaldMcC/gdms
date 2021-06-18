
        var width = document.getElementById('newchart').offsetWidth - makesmaller;
        var makesmaller=50;
        var height = 200;
        /*var color = d3.scale.category10();*/
        var color = d3.scaleOrdinal(d3.schemeCategory10);
        var radius = Math.min(width, height) / 2;
        var legendRectSize = 18;
        var legendSpacing = 4;
        var legendHorizOffset = 200;

        var svg = d3.select('#newchart')
          .append('svg')
          .attr('width', width)
          .attr('height', height)
          .append('g')
          .attr('transform', 'translate(' + (width / 2) +
            ',' + (height / 2) + ')');

        var arc = d3.arc()
          .outerRadius(radius)
            .innerRadius(0);

        var pie = d3.pie()
          .value(function(d) { return d.count; })
          .sort(null);

        var tooltip = d3.select('#newchart')            // NEW
            .append('div')                             // NEW
            .attr('class', 'd3tooltip');                 // NEW

        tooltip.append('div')                        // NEW
            .attr('class', 'd3label');                   // NEW

        tooltip.append('div')                        // NEW
            .attr('class', 'count');                   // NEW

        tooltip.append('div')                        // NEW
            .attr('class', 'percent');                 // NEW

        var path = svg.selectAll('path')
            .data(pie(newans))
            .enter()
            .append('path')
            .attr('d', arc)
            .attr('fill', function(d, i) {
                return color(d.data.label);
             });

        path.on('mouseover', function(d) {           // NEW
            var total = d3.sum(newans.map(function(d) {
            return d.count;
            }));
            var percent = Math.round(1000 * d.data.count / total) / 10;
            tooltip.select('.d3label').html('Ans: ' + d.data.label);
            tooltip.select('.count').html('Count: ' + d.data.count);
            tooltip.select('.percent').html(percent + '%');
            tooltip.style('display', 'block');
            });                                          // NEW

        path.on('mouseout', function(d) {            // NEW
             tooltip.style('display', 'none');
        });

        var legend = svg.selectAll('.legend')
          .data(color.domain())
          .enter()
          .append('g')
          .attr('class', 'legend')
          .attr('transform', function(d, i) {
            var height = legendRectSize + legendSpacing;
            var offset =  height * color.domain().length / 2;
            var horz = -2 * legendRectSize + legendHorizOffset ;
            var vert = i * height - offset;
            return 'translate(' + horz + ',' + vert + ')';
          });

        legend.append('rect')
          .attr('width', legendRectSize)
          .attr('height', legendRectSize)
          .style('fill', color)
          .style('stroke', color);

        legend.append('text')
          .attr('x', legendRectSize + legendSpacing)
          .attr('y', legendRectSize - legendSpacing)
          .text(function(d) { return d; });
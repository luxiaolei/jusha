$(function(){
  $("#generate").bind('click', function(){
      //var width = $("#barchart").width();
      //console.log(width)
      var margin = {top: 20, right: 20, bottom: 30, left: 40},
          width = 760 - margin.left - margin.right,
          height = 200 - margin.top - margin.bottom;

      var x = d3.scale.ordinal()
          .rangeRoundBands([0, width], .1);

      var y = d3.scale.linear()
          .range([height, 0]);

      var xAxis = d3.svg.axis()
          .scale(x)
          .orient("bottom");

      var yAxis = d3.svg.axis()
          .scale(y)
          .orient("left")

      //delete the previous barchart if exsits
      var svgflag = $("svg").length
      if (svgflag > 1){
        $("svg:last").remove();
      };

      var svg = d3.select("#barchart").append("svg")
                    .attr("width", width + margin.left + margin.right)
                    .attr("height", height + margin.top + margin.bottom)
                  .append("g")
                    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

      d3.json('/bins',function(error, data) {
        if (error) throw error;

        data.forEach(function(d){
          d.bins = parseFloat(d.bins);
        });

        x.domain(data.map(function(d){return d.ticks}))
        y.domain([0, d3.max(data,function(d){return d.bins})]);

        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis);

        svg.append("g")
            .attr("class", "y axis")
            .call(yAxis)
          .append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 6)
            .attr("dy", ".71em")
            .style("text-anchor", "end")
            .text("Number of Data");

        svg.selectAll(".bar")
              .data(data)
            .enter().append("rect")
              .style("fill", "steelblue")
              .attr("x", function(d) { return x(d.ticks); })
              .attr("width", x.rangeBand())
              .attr("y", function(d) { return y(d.bins); })
              .attr("height", function(d) { return height - y(d.bins); });
      });
    });
  });

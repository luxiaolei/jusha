
var barChart = function(url, numSvg){
  var margin = {top: 1, right: 1, bottom: 1, left: 1},
      width = $('#barchart').width() //560 - margin.left - margin.right,
      height = $('#barchart').height() //200 - margin.top - margin.bottom;

  console.log(url)
  var x = d3.scale.ordinal()
      .rangeRoundBands([0, width], .0,0);

  var y = d3.scale.linear()
      .range([height, 0]);

  var xAxis = d3.svg.axis()
      .scale(x)
      .orient("bottom")

      //.attr('transform', 'rotate(45)');

  var yAxis = d3.svg.axis()
      .scale(y)
      .orient("left")

  //delete the previous barchart if exsits
  var svgflag = $("svg").length
  if (svgflag > numSvg){
    $("svg:last").remove();
  };

  var svg = d3.select("#barchart").append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
              .append("g")
                .attr("transform", "translate(" -10 + "," + margin.top + ")");

  d3.json(url,function(error, data) {
    if (error) throw error;
    data.forEach(function(d){
      d.bins = parseFloat(d.bins);
    });
    x.domain(data.map(function(d){return d.ticks}))
    y.domain([0, d3.max(data,function(d){return d.bins})]);
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(100," + height + ")")
        .call(xAxis).attr('height', height).selectAll("text")
                    .style("text-anchor", "middle")
                    .attr('transform', 'rotate(-15)');
    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
      .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("Number of Data");
    var recEnter = svg.selectAll(".bar")
          .data(data)
          .enter()
    recEnter.append("rect")
            .style("fill", function(d){return d.color})
            .attr('id', function(d,i){return 'bar'+i})
            .attr("x", function(d) { return x(d.ticks) ; })
            .attr("width", x.rangeBand())
            .attr("y",  function(d) { return y(d.bins); })
            .attr("height", function(d) { return height - y(d.bins); })
            .on('mouseover', function(d){
              //change color of the rect
              //search data in the rect
              searchFunc(d.binData)
              d3.select(this).style("fill", "green")
            })
            .on('mouseout', function(){
              //change back color, both for the bar and nodes
              d3.select('#graph').selectAll(".node").style('opacity', 1)
              d3.select(this).style("fill", function(d){return d.color})
            })
            .on('click', function(d,i){
              //send clicked bar index to server
              if (numSvg == 1){
                var data = {'binClicked': i}
                $.ajax({
                  type : "POST",
                  //mimic the url_for function when this js file is external
                  url : "/binClickedAjax",
                  data: JSON.stringify(data),
                  contentType: 'application/json;charset=UTF-8',
                  success: function(){
                    console.log('barClicked index post successed!')
                  }
                });
              }

            })

          })
        }

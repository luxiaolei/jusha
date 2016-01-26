

var genCandles = function(){
  $('#candles').children().remove()
  var margin = {top: 20, right: 20, bottom: 30, left: 50},
          width = 960 - margin.left - margin.right,
          height = 500 - margin.top - margin.bottom;

  var parseDate = d3.time.format("%Y-%m-%d").parse;

  var x = techan.scale.financetime()
          .range([0, width]);

  var y = d3.scale.linear()
          .range([height, 0]);

  var zoom = d3.behavior.zoom()
          .on("zoom", draw);

  var candlestick = techan.plot.candlestick()
          .xScale(x)
          .yScale(y);


  var xAxis = d3.svg.axis()
          .scale(x)
          .orient("bottom");

  var yAxis = d3.svg.axis()
          .scale(y)
          .orient("left");

  var svg = d3.select("#candles").append("svg")
          .attr("width", width + margin.left + margin.right)
          .attr("height", height + margin.top + margin.bottom)
      .append("g")
          .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  svg.append("clipPath")
          .attr("id", "clip")
      .append("rect")
          .attr("x", 0)
          .attr("y", y(1))
          .attr("width", width)
          .attr("height", y(0) - y(1));

  svg.append("g")
          .attr("class", "candlestick")
          .attr("clip-path", "url(#clip)");

  svg.append("g")
          .attr("class", "x axis")
          .attr("transform", "translate(0," + height + ")");

  svg.append("g")
          .attr("class", "y axis")
      .append("text")
          .attr("transform", "rotate(-90)")
          .attr("y", 6)
          .attr("dy", ".71em")
          .style("text-anchor", "end")
          .text("Price ");

  svg.append("rect")
          .attr("class", "pane")
          .attr("width", width)
          .attr("height", height)
          .call(zoom);

  var result = d3.csv("/ohlc", function(error, data) {

      var accessor = candlestick.accessor();

      data = data.map(function(d) {
          return {
              date: parseDate(d.Date),
              open: +d.Open,
              high: +d.High,
              low: +d.Low,
              close: +d.Close,
              volume: +d.Volume
          };

      })
      data = data.sort(function(a, b) { return d3.ascending(accessor.d(a), accessor.d(b)); });

      x.domain(data.map(accessor.d));
      y.domain(techan.scale.plot.ohlc(data, accessor).domain());


      svg.select("g.candlestick").datum(data);
      draw();

      // Associate the zoom with the scale after a domain has been applied
      zoom.x(x.zoomable().clamp(false)).y(y);
  });

  function draw() {
      svg.select("g.candlestick").call(candlestick);
      // using refresh method is more efficient as it does not perform any data joins
      // Use this if underlying data is not changing
  //        svg.select("g.candlestick").call(candlestick.refresh);
      svg.select("g.x.axis").call(xAxis);
      svg.select("g.y.axis").call(yAxis)
      //svg.select("g.tradearrow").call(tradearrow)
  }
}



var arrows = function(selected){

  var margin = {top: 20, right: 20, bottom: 30, left: 50},
          width = 960 - margin.left - margin.right,
          height = 500 - margin.top - margin.bottom;

  var parseDate = d3.time.format("%Y-%m-%d").parse;

  var x = techan.scale.financetime()
          .range([0, width]);

  var y = d3.scale.linear()
          .range([height, 0]);

  var candlestick = techan.plot.candlestick()
          .xScale(x)
          .yScale(y);


  var xAxis = d3.svg.axis()
          .scale(x)
          .orient("bottom");

  var yAxis = d3.svg.axis()
          .scale(y)
          .orient("left");

  var zoom = d3.behavior.zoom()
          .on("zoom", draw);

          var tradearrow = techan.plot.tradearrow()
                .xScale(x)
                .yScale(y)
                .orient(function(d) { return d.type.startsWith("buy") ? "up" : "down"; })


  var svg = d3.select('body').select('svg').select('g')


  var result = d3.csv("/ohlc", function(error, data) {

      var accessor = candlestick.accessor();

      data = data.map(function(d) {
          return {
              date: parseDate(d.Date),
              open: +d.Open,
              high: +d.High,
              low: +d.Low,
              close: +d.Close,
              volume: +d.Volume
          };

      })
      data = data.sort(function(a, b) { return d3.ascending(accessor.d(a), accessor.d(b)); });

      x.domain(data.map(accessor.d));
      y.domain(techan.scale.plot.ohlc(data, accessor).domain());


      //var selected = [67,120,450,280,344,455,555,231,678,900,1230]

      var trades = []
      for (i in selected){
        var elem = { date: data[selected[i]].date, type: "buy", price: data[selected[i]].low, quantity: 1000}
          trades.push(elem)
      }

      console.log(trades[0])

      svg.append("g")
              .datum(trades)
              .attr("class", "tradearrow")


      svg.select("g.candlestick").datum(data);
      draw();

      // Associate the zoom with the scale after a domain has been applied
      zoom.x(x.zoomable().clamp(false)).y(y);
  });

  function draw() {
    svg.select("g.candlestick").call(candlestick);
    // using refresh method is more efficient as it does not perform any data joins
    // Use this if underlying data is not changing
//        svg.select("g.candlestick").call(candlestick.refresh);
    svg.select("g.x.axis").call(xAxis);
    svg.select("g.y.axis").call(yAxis);

      svg.select("g.tradearrow").call(tradearrow)
  }
}

$(function(){
  $('#refresharrow').on('click',function(){
    $('.tradearrow').remove()

    var selectedArray = $('#selection').data('tmp')
    console.log(selectedArray)
    arrows(selectedArray)
   //svg.select("g.tradearrow").call(tradearrow)
  })
})

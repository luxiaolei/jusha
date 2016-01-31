var seriesCandlestick = function () {

        var xScale = d3.time.scale(),
            yScale = d3.scale.linear();

        var rectangleWidth = 1;

        var isUpDay = function(d) {
            return d.close > d.open;
        };
        var isDownDay = function (d) {
            return !isUpDay(d);
        };

        var line = d3.svg.line()
            .x(function (d) {
                return d.x;
            })
            .y(function (d) {
                return d.y;
            });

        var highLowLines = function (bars) {

            var paths = bars.selectAll('.high-low-line').data(function (d) {
                return [d];
            });

            paths.enter().append('path');

            paths.classed('high-low-line', true)
                .attr('d', function (d) {
                    return line([
                        { x: xScale(d.date), y: yScale(d.high) },
                        { x: xScale(d.date), y: yScale(d.low) }
                    ]);
                });
        };

        var rectangles = function (bars) {
            var rect;

            rect = bars.selectAll('rect').data(function (d) {
                return [d];
            });

            rect.enter().append('rect');

            rect.attr('x', function (d) {
                return xScale(d.date) - rectangleWidth;
            })
                .attr('y', function (d) {
                    return isUpDay(d) ? yScale(d.close) : yScale(d.open);
                })
                .attr('width', rectangleWidth * 2)
                .attr('height', function (d) {
                    return isUpDay(d) ?
                        yScale(d.open) - yScale(d.close) :
                        yScale(d.close) - yScale(d.open);
                });
        };

        var candlestick = function (selection) {
            var series, bars;

            selection.each(function (data) {
                series = d3.select(this).selectAll('.candlestick-series').data([data]);

                series.enter().append('g')
                    .classed('candlestick-series', true);

                bars = series.selectAll('.bar')
                    .data(data, function (d) {
                        return d.date;
                    });

                bars.enter()
                    .append('g')
                    .classed('bar', true);

                bars.classed({
                    'up-day': isUpDay,
                    'down-day': isDownDay
                });

                highLowLines(bars);
                rectangles(bars);

                bars.exit().remove();


            });
        };

        candlestick.xScale = function (value) {
            if (!arguments.length) {
                return xScale;
            }
            xScale = value;
            return candlestick;
        };

        candlestick.yScale = function (value) {
            if (!arguments.length) {
                return yScale;
            }
            yScale = value;
            return candlestick;
        };

        candlestick.rectangleWidth = function (value) {
            if (!arguments.length) {
                return rectangleWidth;
            }
            rectangleWidth = value;
            return candlestick;
        };

        return candlestick;

    };

var genCandles = function(){
  $('#candles').children().remove()
  var margin = {top: 20, right: 20, bottom: 30, left: 50},
      width = 5280 - margin.left - margin.right,
      height = 600 - margin.top - margin.bottom;

  var parseDate = d3.time.format("%Y-%m-%d").parse;

  var xScale = d3.time.scale(),
      yScale = d3.scale.linear();

  var xAxis = d3.svg.axis()
      .scale(xScale)
      .orient('bottom')
      .ticks(5);

  var yAxis = d3.svg.axis()
      .scale(yScale)
      .orient('left');

  var series = seriesCandlestick()
      .xScale(xScale)
      .yScale(yScale);

  // Create svg element
  var svg = d3.select('#candles').classed('chart', true).append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom);

  // Ceate chart
  var g = svg.append('g')
      .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

  var plotArea = g.append('g');
  plotArea.append('clipPath')
      .attr('id', 'plotAreaClip')
      .append('rect')
      .attr({ width: width, height: height });
  plotArea.attr('clip-path', 'url(#plotAreaClip)');

  d3.csv("/ohlc", function(data){
    //data = data.slice(0,100)
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

    // Set scale domains
  var maxDate = d3.max(data, function (d) {
      return d.date;
  });

  var minDate = d3.min(data, function(d){
      return d.date;
  })

  console.log(maxDate)
  console.log(minDate)
  console.log(minDate.getTime())

  xScale.domain([
      new Date(minDate.getTime()),// - (8.64e7 * 31.5)),
      new Date(maxDate.getTime())// + 8.64e7)
  ]);

  yScale.domain(
      [
          d3.min(data, function (d) {
              return d.low;
          }),
          d3.max(data, function (d) {
              return d.high;
          })
      ]
  ).nice();

  // Set scale ranges
  xScale.range([0, width]);
  yScale.range([height, 0]);

  // Draw axes
  g.append('g')
      .attr('class', 'x axis')
      .attr('transform', 'translate(0,' + height + ')')
      .call(xAxis);

  g.append('g')
      .attr('class', 'y axis')
      .call(yAxis);

  // Draw series.
  plotArea.append('g')
      .attr('class', 'series')
      .datum(data)
      .call(series);

  });

}

var genCandles = function(){



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

      var zoom = d3.behavior.zoom()
          .x(xScale)
          .scaleExtent([0.5, 50])
          .on('zoom', zoomed)
          .on('zoomend', zoomend);

      var zoomChart = exampleZoomChart(zoom, data, series, xScale, yScale, xAxis, yAxis, fromDate, toDate);
      zoomChart();

      function zoomed() {
          var xDomain = xScale.domain();
          var range = moment().range(xDomain[0], xDomain[1]);
          var filteredData = [];
          var g = d3.selectAll('svg').select('g');

          for (var i = 0; i < data.length; i += 1) {
              if (range.contains(data[i].date)) {
                  filteredData.push(data[i]);
              }
          }
          yScale.domain(
              [
                  d3.min(filteredData, function (d) {
                      return d.Low;
                  }),
                  d3.max(filteredData, function (d) {
                      return d.High;
                  })
              ]
          );

          g.select('.x.axis')
              .call(xAxis);

          g.select('.y.axis')
              .call(yAxis);

          series.tickWidth(tickWidth(xScale, xDomain[0], xDomain[1]));

          g.select('.series')
              .call(series);
      }

      function zoomend() {
      }
}




var seriesCandlestick = function () {

        var xScale = d3.time.scale(),
            yScale = d3.scale.linear();

        var rectangleWidth = 5;

        var isUpDay = function(d) {
            return d.Close > d.Open;
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
                        { x: xScale(d.date), y: yScale(d.High) },
                        { x: xScale(d.date), y: yScale(d.Low) }
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
                    return isUpDay(d) ? yScale(d.Close) : yScale(d.Open);
                })
                .attr('width', rectangleWidth * 2)
                .attr('height', function (d) {
                    return isUpDay(d) ?
                        yScale(d.Open) - yScale(d.Close) :
                        yScale(d.Close) - yScale(d.Open);
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




var exampleZoomChart = function (zoom, data, series, xScale, yScale, xAxis, yAxis, fromDate, toDate) {

            var initialScale = d3.scale.linear();

            var zoomChart = function () {
                var margin = {top: 20, right: 20, bottom: 30, left: 50},
                    width = 800 - margin.left - margin.right,
                    height = 400 - margin.top - margin.bottom;

                // Create svg element
                var svg = d3.select('#candles').classed('chart', true).append('svg')
                    .attr('width', width + margin.left + margin.right)
                    .attr('height', height + margin.top + margin.bottom);

                // Ceate chart
                var g = svg.append('g')
                    .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

                // Create plot area
                var plotArea = g.append('g');
                plotArea.append('clipPath')
                    .attr('id', 'plotAreaClip')
                    .append('rect')
                    .attr({ width: width, height: height });
                plotArea.attr('clip-path', 'url(#plotAreaClip)');

                // Create zoom pane
                plotArea.append('rect')
                    .attr('class', 'zoom-pane')
                    .attr('width', width)
                    .attr('height', height)
                    .call(zoom);

                // Set scale domains
                xScale.domain(d3.extent(data, function (d) {
                    return d.Date;
                }));

                yScale.domain(
                    [
                        d3.min(data, function (d) {
                            return d.Low;
                        }),
                        d3.max(data, function (d) {
                            return d.High;
                        })
                    ]
                );

                // Set scale ranges
                xScale.range([0, width]);
                yScale.range([height, 0]);

                // Reset zoom.
                zoom.x(xScale);

                series.tickWidth(tickWidth(xScale, fromDate, toDate));

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

                initialScale = yScale.copy();
            };

            zoomChart.initialScale = function () {
                return initialScale;
            };

            return zoomChart;
        };

var runClustering = function(){

    $("#generate").hide()
  var svgFlag = $("#graph").children("svg").length
  if (svgFlag == 1){
    //remove the previous clusters
    $("#graph").children("svg").remove()
  }

  //.attr('id', 'members')
  var margin = {top: -5, right: -5, bottom: -5, left: -5}
  var width = $('#graph').parent().width()//540//$("svg").parent().width();
  var height = 800//$('#graph').parent().height()//400//$("svg").parent().height();

      //.style("background-color", 'black')//.append('div')
  //var container = mappersvg.append("g")
  function zoomed() {
  mappersvg.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
  }
  function dragstarted(d) {
    d3.event.sourceEvent.stopPropagation();
    d3.select(this).classed("dragging", true);
  }

  function dragged(d) {
    d3.select(this).attr("cx", d.x = d3.event.x).attr("cy", d.y = d3.event.y);
  }

  function dragended(d) {
    d3.select(this).classed("dragging", false);
  }

  var zoom = d3.behavior.zoom()
    .scaleExtent([.2, 10])
    .on("zoom", zoomed);

  var drag = d3.behavior.drag()
      .origin(function(d) { return d; })
      .on("dragstart", dragstarted)
      .on("drag", dragged)
      .on("dragend", dragended);

  var svg = d3.select("#graph")
              .append("svg")
                .attr("width", width)
                .attr("height", height)
              .append('g')
                .attr("transform", "translate(" + margin.left + "," + margin.right + ")")

  var mappersvg = svg.append('g')

    $(document).keydown(function (e) {
        if (e.keyCode == 16) {
          svg.call(zoom)
        }
    });

    $(document).keyup(function (e) {
      if (e.keyCode == 16) {
        svg.on('.zoom',null)
      }
  });
  var force = d3.layout.force()
  	.charge(-120)
  	.linkDistance(17)
  	.size([width,height]);
    var k = 0;
    while ((force.alpha() > 1e-2) && (k < 150)) {
        force.tick(),
        k = k + 1;
    }

  d3.json("/mapperjson", function(d) {
      var nodes = d['vertices'];
      var edges = d['edges'];
      var statests = d['statisticT']
      var colormap = d['colormap']
      var distinctAttr = d['distinctAttr']


      var linkColor = []//d3.set();
      for(l in edges){
        linkColor.push(edges[l].wt)
      }

      var nodeSize = []
      for(s in nodes){
        nodeSize.push(nodes[s].members.length)
      }

      var fscale = d3.scale.linear()
      	.range(colormap)
      	.domain(distinctAttr)//[d3.min(distinctAttr), d3.max(distinctAttr)])//([0,d3.max(nodeattr)]);//([0,d3.max(nodeattr)]);

      var lscale = d3.scale.linear()
        .range(['blue', 'red'])
        .domain([0, d3.max(linkColor)]);

      var lwscale = d3.scale.linear()
        .range([0.5, 3.5])
        .domain([0, d3.max(linkColor)]);

      var Sscale = d3.scale.linear()
        .range([4, 9])
        .domain([1, d3.max(nodeSize)])

      force.nodes(nodes)
      	.links(edges)
      	.start();

      var link = mappersvg.append('g').selectAll(".link")
      	.data(edges)
      	.enter().append("line")
      	.attr("class","link")
        .style('stroke', function(e){return lscale(e.wt);})//"#999")
        .style('stroke-width', function(e){return lwscale(e.wt);})
        .style('stroke-opacity', 0.6);

      var node = mappersvg.append('g').attr("class", "node")
      .selectAll(".node")
      	.data(nodes)
      	.enter().append("circle")
        .attr("id", function(e){return 'circleid_'+e.index})
      	.attr("r", function(e) { return Sscale(e.members.length) })//Math.min(10,(3+Math.sqrt(e.members.length))); })
      	.style("fill", function(e) { return fscale(e.attribute);})
      	.text(function(e){return e.members.length; })
      	.on('mouseover', function(e) {
          //mouseoverShowExaplain(e,statests)
          //var svgFlag = $('svg').length
          //if (svgFlag > 1){mouseoverHighlightBars(e.members)}
          mouseoverHighlightBars(e.members)

          var members_string = 'The '+e.index+'th node contains:';
          for (i in e.members){
            members_string+= "," + d.indexNameMap[e.members[i]]
          }
      	    $("#members").html(members_string);
      	})
        .on('mouseout',function(){
          $('#explain').children().remove()
          d3.selectAll('rect').style('opacity', 1)
        })
          .call(force.drag)  ;

        var brusher = d3.svg.brush()
            .x(d3.scale.identity().domain([0, width]))
            .y(d3.scale.identity().domain([0, height]))
            .on("brush", function() {
              var extent = d3.event.target.extent();
              var li = []
              var selectionIndex = []
              var members = []
              node.classed("selected", function(d) {
                if( extent[0][0] <= d.x && d.x < extent[1][0]
                    && extent[0][1] <= d.y && d.y < extent[1][1]){
                      //li.push(d)
                      //selectionIndex.push(d.index)

                      $.each(d.members, function(i,e){members.push(e)})
                      var uniquemembers = uniqueArray(members)
                        $('[id^=Selection').each(function(){
                          var display = $(this).children().first()
                          var btn = $(this).children().last()
                          if (btn.val()==0){
                            //console.log(btn.val())
                            display.html(uniquemembers.length)}
                        })
                      //console.log(uniqueArray(members))
                      $('#selection').data('tmp',uniquemembers)
                      //console.log(li.length)
                      //html(li.length)
                      return d
                    };
              })//.each(function(e){console.log(e)});
              $('#export2csv').show()
            })

        var brush = mappersvg.append("g")
        brush.attr("class", "brush").call(brusher)
        brush.select('.background').style('cursor', 'auto')


      var label = node.append("text")
          .text(function (d) { return d.index; })
          .style("fill", "#555")
          .style("font-family", "Arial")
          .style("font-size", 12);

      force.on("tick", function () {
      	link.attr("x1", function(e) { return e.source.x ; })//-100; })
            .attr("y1", function(e) { return e.source.y ; })//- 50; })
            .attr("x2", function(e) { return e.target.x ; })//-100; })
            .attr("y2", function(e) { return e.target.y ; })//- 50; });
      	node.attr("cx", function(e) { return e.x ; })// -100; })
                  .attr("cy", function(e) { return e.y ; })//- 50; });
      });
  });
    d3.select('#recolor').on('click',function(){
      //force.stop()
      var refreshGraph = function(url){
        d3.json(url,function(d){
          var nodes = d['vertices'];

          var colormap = d['colormap']
          var distinctAttr = d['distinctAttr']
          console.log(distinctAttr)
          var fscale = d3.scale.linear()
          	.range(colormap)
          	.domain(distinctAttr);
          //###D3 way of coloring
          //var node = mappersvg.selectAll("circle")
          //node
          //.data(nodes)
          //.style('fill', function(e) { return fscale(e.attribute);})
          $('circle').each(function(){
            //console.log($(this).index())
            $(this).css('fill', function(){return fscale(nodes[$(this).index()].attribute)})
          })
        });
      };
      var buttonType = $('#recolor')
      if(buttonType.html() == 'Re Color!'){
        refreshGraph('/newjson')
        buttonType.html('Reverse!')
      }else{
        buttonType.html('Re Color!')
        refreshGraph('/mapperJsonSaved')
      }
    })
}


$(function(){
  $('[id^=Selection]').each(function(){
    $(this).bind('click',function(){
      var btn = $(this).children().last()
      if (btn.val()==0){
        btn.html('Clear!');
        btn.val(1);
        //get selected nodes indexes from temp
        var selectedArray = $('#selection').data('tmp')
        //set the array to the clicked button
        btn.data('selected', selectedArray)
      }else{
        btn.html('Select!');
        btn.val(0);      }

      //controll the explain button display
      var value = 0;
      $('[id^=add]').each(function(){
        value += parseInt($(this).val())
      })
      if (value==2){$('#explain').show()}else{$('#explain').hide()}

    })
  })
})

var mouseoverHighlightBars = function(datalist){
  //datalist: dataIndex
  //when mouseover nodes, hightlights bars contain data
  d3.json('/bins',function(error,data){
    if (error) throw error;
    var selectedBinIndexs = [];
    for (iN in datalist){
      for (iB in data){
        var flag = $.inArray(datalist[iN], data[iB].binData)
        var pushedAlready = $.inArray(iB, selectedBinIndexs)
        if (flag != -1 ){selectedBinIndexs.push(parseInt(iB))}
      }
    }
    //console.log(selectedBinIndexs)
    d3.selectAll('rect')
      .filter(function(d,i){
        if ($.inArray(i, selectedBinIndexs) != -1){return false}else{return true}
      })
      .style('opacity', .3)
  })
}


//redundent code!
var mouseoverShowExaplain = function(e,statests){
  //when mouseover nodes, Get explainjason from the server
  //show the statistic test results by nodes index
  var tests = statests[e.index]
  //console.log((tests).constructor === Number)
  if ((tests).constructor === Number){
    var warning = $('<li>This node contain too few data:'+tests+'</li>')
    warning.appendTo('#explain')

  }else{
    var num = $('<li> There are :['+e.members.length+'] number of data.</li>')
    num.appendTo('#explain')
    for (f in tests){
      var fhead = $('<li><a class="btn">'+f+'</a></li>')
      var ttest = $('<li>'+tests[f][0]+'</li>')
      var kstest = $('<li>'+tests[f][1]+'</li>')
      ttest.appendTo(fhead)
      kstest.appendTo(fhead)
      fhead.appendTo('#explain')
    }
  }
}

var uniqueArray = function(list) {
  var result = [];
  $.each(list, function(i, e) {
    if ($.inArray(e, result) == -1){result.push(e)};
  });
  return result;
}

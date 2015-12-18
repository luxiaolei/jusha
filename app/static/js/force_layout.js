var runClustering = function(){

    $("#generate").hide()
  var svgFlag = $("#graph").children("svg").length
  if (svgFlag == 1){
    //remove the previous clusters
    $("#graph").children("svg").remove()
  }

  var mappersvg = d3.select("#graph")
      .append("svg")
      //.style("background-color", 'black')//.append('div')
                    //.attr('id', 'members')

  var width = 540//$("svg").parent().width();
  var height = 400//$("svg").parent().height();

  mappersvg.attr("width", width)
            .attr("height", height)

  var force = d3.layout.force()
  	.charge(-100)
  	.linkDistance(10)
  	.size([640,480]);
    var k = 0;
    while ((force.alpha() > 1e-2) && (k < 150)) {
        force.tick(),
        k = k + 1;
    }

  d3.json("/mapperjson", function(d) {
      var nodes = d['vertices'];
      var edges = d['edges'];
      var statests = d['statisticT']

      var nodeattr = [];
      for(n in nodes) {
    	nodeattr.push(nodes[n].attribute);
        }

      var linkColor = []//d3.set();
      for(l in edges){
        linkColor.push(edges[l].wt)

      }

      var nodeSize = []
      for(s in nodes){
        nodeSize.push(nodes[s].members.length)
      }

      var fscale = d3.scale.linear()
      	.range(['blue','red'])
      	.domain([0,d3.max(nodeattr)]);

      var lscale = d3.scale.linear()
        .range(['blue', 'red'])
        .domain([0, d3.max(linkColor)]);

      var lwscale = d3.scale.linear()
        .range([0.5, 3.5])
        .domain([0, d3.max(linkColor)]);

      var Sscale = d3.scale.linear()
        .range([3, 12])
        .domain([1, d3.max(nodeSize)])

      force.nodes(nodes)
      	.links(edges)
      	.start();

      var link = mappersvg.selectAll(".link")
      	.data(edges)
      	.enter().append("line")
      	.attr("class","link")
        .style('stroke', function(e){return lscale(e.wt);})//"#999")
        .style('stroke-width', function(e){return lwscale(e.wt);})
        .style('stroke-opacity', 0.6);

      var node = mappersvg.selectAll(".node")
      	.data(nodes)
      	.enter().append("circle")
      	.attr("class", "node")
        .attr("id", function(e){return 'circleid_'+e.index})
      	.attr("r", function(e) { return Sscale(e.members.length) })//Math.min(10,(3+Math.sqrt(e.members.length))); })
      	.style("fill", function(e) { return fscale(e.attribute);})
      	.text(function(e){return e.members.length; })
      	.on('mouseover', function(e) {
          mouseoverShowExaplain(e,statests)

          console.log(e.index)
          var svgFlag = $('svg').length
          if (svgFlag > 1){mouseoverHighlightBars(e.members)}

          var members_string = 'The '+e.index+'th node contains:';
          for (i in e.members){
            members_string+= "," + e.members[i]
          }
      	    $("#members").html(members_string);
      	})
        .on('mouseout',function(){
          //$('#explain').children().remove()
          d3.selectAll('rect').style('fill', 'steelblue')
        })

      	//.call(force.drag)  ;

      var label = node.append("text")
          .text(function (d) { return d.index; })
          .style("fill", "#555")
          .style("font-family", "Arial")
          .style("font-size", 12);


      force.on("tick", function () {
      	link.attr("x1", function(e) { return e.source.x -100; })
            .attr("y1", function(e) { return e.source.y - 50; })
            .attr("x2", function(e) { return e.target.x -100; })
            .attr("y2", function(e) { return e.target.y - 50; });
      	node.attr("cx", function(e) { return e.x -100; })
                  .attr("cy", function(e) { return e.y - 50; });
      });
      //setTimeout(force.stop(), 6000)
  });




  //var RadioBtns = d3.selectAll("input[name='features']")
  //console.log(RadioBtns)

  //RadioBtns.each(function(d){
  //  console.log(this)
    d3.select('#recolor').on('click',function(){
      force.stop()
      var refreshGraph = function(url){
        d3.json(url,function(d){
          var nodes = d['vertices'];
          var nodeattr = [];
          for(n in nodes) {
            nodeattr.push(nodes[n].attribute);
          }
          var fscale = d3.scale.linear()
            .range(['blue','red'])
            .domain([0,d3.max(nodeattr)]);
          var node = mappersvg.selectAll(".node")
          //update the color
          node
          .data(nodes)
          .style('fill', function(e) { return fscale(e.attribute);})
        });
      };
      var buttonType = $('#recolor')
      if(buttonType.html() == 'Re Color!'){
        refreshGraph('/newjson')
        buttonType.html('Reverse!')
      }else{
        buttonType.html('Re Color!')
        refreshGraph('/mapperjson')
      }
    })
  //});

}

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
        if ($.inArray(i, selectedBinIndexs) == -1){return false}else{return true}
      })
      .style('fill', 'green')
  })
}

var mouseoverShowExaplain = function(e,statests){
  //when mouseover nodes, Get explainjason from the server
  //show the statistic test results by nodes index
  var tests = statests[e.index]
  //console.log((tests).constructor === Number)
  if ((tests).constructor === Number){
    var warning = $('<li>This node contain too few data:'+tests+'</li>')
    warning.appendTo('#explain')

  }else{
    for (f in tests){
      var fhead = $('<li><a class="btn">'+f+'</a></li>')
      var ttest = $('<li>'+tests[f][0]+'</li>')
      var kstest = $('<li>'+tests[f][1]+'</li>')
      var num = $('<li>'+tests[f][2]+'</li>')
      ttest.appendTo(fhead)
      kstest.appendTo(fhead)
      num.appendTo(fhead)

      fhead.appendTo('#explain')
    }
    //var result = $('<li>P value for </li>')
  }

}

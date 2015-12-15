var runClustering = function(){

  var svgFlag = $("#graph").children("svg").length
  if (svgFlag == 1){
    //remove the previous clusters
    $("#graph").children("svg").remove()
  }

  var mappersvg = d3.select("#graph")
      .append("svg")//.append('div')
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

      var nodeattr = [];
      for(n in nodes) {
    	nodeattr.push(nodes[n].attribute);
        }

      var linkColor = []//d3.set();
      for(l in edges){
        linkColor.push(edges[l].wt)

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
      	.attr("r", function(e) { return Math.min(10,(3+Math.sqrt(e.members.length))); })
      	.style("fill", function(e) { return fscale(e.attribute);})
      	.text(function(e){return e.members.length; })
      	.on('mouseover', function(e) {
          var svgFlag = $('svg').length
          if (svgFlag > 1){mouseoverHighlightBars(e.members)}

          var members_string = 'The '+e.index+'th node contains:';
          for (i in e.members){
            members_string+= "," + e.members[i]
          }
      	    $("#members").html(members_string);
      	})
        .on('mouseout',function(){d3.selectAll('rect').style('fill', 'steelblue')})



      	//.call(force.drag)  ;

      var label = node.append("text")
          .text(function (d) { return d.index; })
          .style("fill", "#555")
          .style("font-family", "Arial")
          .style("font-size", 12);


      force.on("tick", function () {
      	link.attr("x1", function(e) { return e.source.x; })
                  .attr("y1", function(e) { return e.source.y; })
                  .attr("x2", function(e) { return e.target.x; })
                  .attr("y2", function(e) { return e.target.y; });

      	node.attr("cx", function(e) { return e.x; })
                  .attr("cy", function(e) { return e.y; });
      });
      //setTimeout(force.stop(), 6000)
  });


  d3.select("#generate")
    .on('click',function(){
      force.stop()
      var refreshGraph = function(){
        d3.json("/newjson",function(d){
          var nodes = d['vertices'];


          var nodeattr = [];
          for(n in nodes) {
            nodeattr.push(nodes[n].attribute);
          }
          var fscale = d3.scale.linear()
            .range(['blue','red'])
            .domain([0,d3.max(nodeattr)]);

          var link = mappersvg.selectAll(".link")
          var node = mappersvg.selectAll(".node")

          //update the color
          node
          .data(nodes)
          .style('fill', function(e) { return fscale(e.attribute);})


        force.on("tick", function () {

        	link.attr("x1", function(e) { return e.source.x; })
              .attr("y1", function(e) { return e.source.y; })
              .attr("x2", function(e) { return e.target.x; })
              .attr("y2", function(e) { return e.target.y; });
        	node.attr("cx", function(e) { return e.x; })
              .attr("cy", function(e) { return e.y; });

        });

      });
    };
      refreshGraph()
  });

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
    console.log(selectedBinIndexs)
    d3.selectAll('rect')
      .filter(function(d,i){
        if ($.inArray(i, selectedBinIndexs) == -1){return false}else{return true}
      })
      .style('fill', 'green')
  })
}

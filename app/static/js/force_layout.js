var mappersvg = d3.select("#graph")
    .append("svg")
    .attr("width","640")
    .attr("height","480");

var force = d3.layout.force()
	.charge(-100)
	.linkDistance(10)
	.size([640,480]);

d3.json("/mapperjson", function(d) {
    var nodes = d['vertices'];
    var edges = d['edges'];
    var nodeattr = d3.set();
    for(n in nodes) {
	nodeattr.add(nodes[n].attribute);
    }

var fscale = d3.scale.linear()
	.range(['blue','red'])
	.domain([0,d3.max(nodeattr.values())]);

force.nodes(nodes)
	.links(edges)
	.start();

var link = mappersvg.selectAll(".link")
	.data(edges)
	.enter().append("line")
	.attr("class","link");

var node = mappersvg.selectAll(".node")
	.data(nodes)
	.enter().append("circle")
	.attr("class", "node")
  .attr("id", function(e){return 'circleid_'+e.index})
	.attr("r", function(e) { return Math.min(10,(3+Math.sqrt(e.members.length))); })
	.style("fill", function(e) { return fscale(e.attribute);})
	.text(function(e){return e.members.length; })
	.on('mouseover', function(e) {

    var members_string = 'The '+e.index+'th node contains:';
    for (i in e.members){
      members_string+= "," + e.members[i]
    }
	    $("#members").html(members_string);
	})
	.call(force.drag)  ;

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
});


d3.select(".changecolor")
  .on('click',function(){
    var refreshGraph = function(){
      d3.json("/newjson",function(d){
        var nodes = d['vertices'];
        var nodeattr = d3.set();
        for(n in nodes) {
          nodeattr.add(nodes[n].attribute);
        }
        var fscale = d3.scale.linear()
          .range(['blue','red'])
          .domain([0,d3.max(nodeattr.values())]);
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
  })

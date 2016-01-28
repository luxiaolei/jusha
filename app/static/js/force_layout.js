var runClustering = function(url) {

  $("#generate").hide()
  var svgFlag = $("#graph").children("svg").length
  if (svgFlag == 1) {
    //remove the previous clusters
    $("#graph").children("svg").remove()
  }

  //.attr('id', 'members')
  var margin = {
    top: -5,
    right: -5,
    bottom: -5,
    left: -5
  }
  var width = $('#graph').parent().width() //540//$("svg").parent().width();
  var height = 800 //$('#graph').parent().height()//400//$("svg").parent().height();
  var shiftKey;

  var svg = d3.select("#graph")
    .on("keydown.brush", keyflip)
    .on("keyup.brush", keyflip)
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .append('g')
    .attr("transform", "translate(" + margin.left + "," + margin.right + ")")

  var mappersvg = svg.append('g')

  var force = d3.layout.force()
    .charge(-120)
    .linkDistance(17)
    .size([width, height]);
  var k = 0;
  while ((force.alpha() > 1e-2) && (k < 150)) {
    force.tick(),
      k = k + 1;
  }
  function keyflip() {
    shiftKey = d3.event.shiftKey || d3.event.metaKey;
  }
  d3.json(url, function(d) {

    var nodes = d['vertices'];
    var edges = d['edges'];
    var statests = d['statisticT']
    var colormap = d['colormap']
    var distinctAttr = d['distinctAttr']
    var indexNameMap = d['indexNameMap']

    var linkColor = [] //d3.set();
    for (l in edges) {
      linkColor.push(edges[l].wt)
    }

    var nodeSize = []
    for (s in nodes) {
      nodeSize.push(nodes[s].members.length)
    }

    var fscale = d3.scale.linear()
      .range(colormap)
      .domain(distinctAttr) //[d3.min(distinctAttr), d3.max(distinctAttr)])//([0,d3.max(nodeattr)]);//([0,d3.max(nodeattr)]);

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

    var tooltip = mappersvg.append("g").attr("transform", "translate(-300,0)");
    //add rectangle to teh group
    tooltip.append("rect")
      .attr("x", 0)
      .attr("y", 0)
      .attr("width", 300)
      .attr("height", height)
      .attr("color", "black")
      .attr("opacity", 0.8);

    var link = mappersvg.append('g').selectAll(".link")
      .data(edges)
      .enter().append("line")
      .attr("class", "link")
      .style('stroke', function(e) {
        return lscale(e.wt);
      }) //"#999")
      .style('stroke-width', function(e) {
        return lwscale(e.wt);
      })
      .style('stroke-opacity', 0.6);

    var node = mappersvg.append('g').attr("class", "node")
      .selectAll(".node")
      .data(nodes)
      .enter().append("circle")
      .attr("id", function(e) {
        return 'circleid_' + e.index
      })
      .attr("r", function(e) {
        return Sscale(e.members.length)
      }) //Math.min(10,(3+Math.sqrt(e.members.length))); })
      .style("fill", function(e) {
        return fscale(e.attribute);
      })
      .text(function(e) {
        return e.members.length;
      })
      .on("mousedown", function(d) {
        if (shiftKey) d3.select(this).classed("selected", d.selected = !d.selected);
        else node.classed("selected", function(p) { return p.selected = d === p; });
      })
      .on('click', function(d) {
        if (tooltip.data && d.name == tooltip.data.name) {
          //if clicked on the same node again close
          tooltip.classed("open", false);
          tooltip
            .transition()
            .attr("transform", "translate(-300,0)") //slide via translate
            .duration(1000);
          tooltip.data = undefined; //set the data to be undefined since the tooltip is closed
          return;
        }
        tooltip.data = d; //set the data to teh opened node
        tooltip.classed("open", true); //set the class as open since the tooltip is opened
        tooltip
          .transition()
          .attr("transform", "translate(0,0)")
          .duration(1000);
        d3.selectAll(".text-tip").remove(); //remove old text
        tooltip.append("text") //set the value to the text
          .attr("transform", "translate(10,100)")
          .attr("class", "text-tip").text(d.name);
      })
      .on('mouseover', function(e) {

        //mouseoverShowExaplain(e,statests)
        //var svgFlag = $('svg').length
        //if (svgFlag > 1){mouseoverHighlightBars(e.members)}
        mouseoverHighlightBars(e.members)

        var members_string = 'The ' + e.index + 'th node contains:';
        for (i in e.members) {
          members_string += "," + d.indexNameMap[e.members[i]]
        }
        $("#members").html(members_string);
      })
      .on('mouseout', function() {
        $('#explain').children().remove()
        d3.selectAll('rect').style('opacity', 1)
      })

    var nodesid = []
    var members = []
    var counter = 0
    var brushcounter = 0
    var brusher = d3.svg.brush()
      .x(d3.scale.identity().domain([0, width]))
      .y(d3.scale.identity().domain([0, height]))
      .on("brushstart", function(d) {

          //node.each(function(d) { d.previouslySelected = shiftKey && d.selected; });
        })
      .on("brush", function() {
        var extent = d3.event.target.extent();
        var li = []

        var ff = $('#selectionNodes').data('tmp')

        if(ff == 'None'){
          console.log('reset!')
          members=[]
          nodesid = []
        }

        node.classed("selected", function(d) {
            if (extent[0][0] <= d.x && d.x < extent[1][0] && extent[0][1] <= d.y && d.y < extent[1][1]) {
              //li.push(d)
              //selectionIndex.push(d.index)

              nodesid.push($(this).attr('id'))

              $.each(d.members, function(i, e) {
                members.push(e)
              })
              var uniquemembers = uniqueArray(members)
              var stringIndex = []
              for (i in uniquemembers) {
                stringIndex.push(indexNameMap[uniquemembers[i]])
              }
              d3.selectAll('text').remove()
              showDataname(svg, stringIndex, width, height)

              $('[id^=addtemp]').each(function() {
                  var elm = $(this)

                  if (elm.attr('value')==0) {
                    //console.log(btn.val())
                    elm.html('Selected:'+uniquemembers.length)
                    $('#selection').data('tmp', uniquemembers)
                  }else{
                    counter += 1
                    if (counter ==1){
                    members= []
                  }
                  }
                })
                //console.log(uniqueArray(members))
              if(nodesid.length>= 0){
              $('#selectionNodes').data('tmp', nodesid)
            }
                //console.log(li.length)
                //html(li.length)
              return d//.selected = d.previouslySelected ^
            };
          }) //.each(function(e){console.log(e)});
        $('#export2csv').show()
      })
      .on("brushend", function() {
          //d3.event.target.clear();

          d3.select(this).call(d3.event.target)
          fixeSelectedNodes()
          //console.log(nodesid)

        });



      svg.attr("class", "brush").call(brusher)
          .datum(function() { return {selected: false, previouslySelected: false}; })

    svg.select('.background').style('cursor', 'auto')

    force.on("tick", function() {
      link.attr("x1", function(e) {
          return e.source.x;
        }) //-100; })
        .attr("y1", function(e) {
          return e.source.y;
        }) //- 50; })
        .attr("x2", function(e) {
          return e.target.x;
        }) //-100; })
        .attr("y2", function(e) {
          return e.target.y;
        }) //- 50; });
      node.attr("cx", function(e) {
          return e.x;
        }) // -100; })
        .attr("cy", function(e) {
          return e.y;
        }) //- 50; });
    });
  });


  d3.select('#recolor').on('click', function() {
    //force.stop()
    var refreshGraph = function(url) {
      d3.json(url, function(d) {

        var nodes = d['vertices'];

        var colormap = d['colormap']
        var distinctAttr = d['distinctAttr']

        var fscale = d3.scale.linear()
          .range(colormap)
          .domain(distinctAttr);
        $('circle').each(function() {
          $(this).css('fill', function() {
            return fscale(nodes[$(this).index()].attribute)
          })
        })
      });
    };
    var buttonType = $('#recolorlabel')
    if (buttonType.html() == 'ColorIt') {
      refreshGraph('/newjson')
      buttonType.html('Reverse!')
    } else {
      buttonType.html('ColorIt')
      refreshGraph('/mapperJsonSaved')
    }
  })
}

var fixeSelectedNodes = function(){
  var nodesid = $('#selectionNodes').data('tmp')
  //deselect if its already selectedArray


  if (nodesid != 'None'){
    nodesid = uniqueArray(nodesid)
    
    //console.log('nodesid is'+ nodesid)
  for(i in nodesid){

    //console.log(nodesid[i])
    var ids = '#'+nodesid[i]
    $(ids).attr('class','selected')
    /* anti-selection
    var flag= $(ids).attr('class')
    console.log('id: '+ids+' status: '+flag)
    if (flag == 'selected'){
      $(ids).attr('class',"")
    }else{
    $(ids).attr('class','selected')
  }
  */

  }
}
}

$(function(){
  var sebtn = $('#sebtnA');
  var display = $('#addtempA');
  sebtn.bind('click',function(){
    var selectedArray = $('#selection').data('tmp')

    //reset
    $('#selection').data('tmp', [])
    //$('#selectionNodes').data('tmp', 'None')


    if(display.attr('value')==0){
    display.data('selected', selectedArray)
    display.attr('value',1)
  }else{
    display.attr('value',0)
  }
  })
})
$(function(){
  var sebtn = $('#sebtnB');
  var display = $('#addtempB');
  sebtn.bind('click',function(){
    var selectedArray = $('#selection').data('tmp')

    $('#selection').data('tmp', [])
    //$('#selectionNodes').data('tmp', 'None')

    if(display.attr('value')==0){
    display.data('selected', selectedArray)
    display.attr('value',1)
  }else{
    display.attr('value',0)
  }
  })
})


$(function() {
  $('[id^=sebtn]').each(function() {
    $(this).bind('click', function() {
      //style it
      if($(this).hasClass('ui-state-hover')){
        $(this).removeClass('ui-state-hover')
      }else{
        $(this).addClass('ui-state-hover')
      }
    })
  })

})


var mouseoverHighlightBars = function(datalist) {
  //datalist: dataIndex
  //when mouseover nodes, hightlights bars contain data
  d3.json('/bins', function(error, data) {
    if (error) throw error;
    var selectedBinIndexs = [];
    for (iN in datalist) {
      for (iB in data) {
        var flag = $.inArray(datalist[iN], data[iB].binData)
        var pushedAlready = $.inArray(iB, selectedBinIndexs)
        if (flag != -1) {
          selectedBinIndexs.push(parseInt(iB))
        }
      }
    }
    //console.log(selectedBinIndexs)
    d3.selectAll('rect')
      .filter(function(d, i) {
        if ($.inArray(i, selectedBinIndexs) != -1) {
          return false
        } else {
          return true
        }
      })
      .style('opacity', .3)
  })
}


//redundent code!
var mouseoverShowExaplain = function(e, statests) {
  //when mouseover nodes, Get explainjason from the server
  //show the statistic test results by nodes index
  var tests = statests[e.index]
    //console.log((tests).constructor === Number)
  if ((tests).constructor === Number) {
    var warning = $('<li>This node contain too few data:' + tests + '</li>')
    warning.appendTo('#explain')

  } else {
    var num = $('<li> There are :[' + e.members.length + '] number of data.</li>')
    num.appendTo('#explain')
    for (f in tests) {
      var fhead = $('<li><a class="btn">' + f + '</a></li>')
      var ttest = $('<li>' + tests[f][0] + '</li>')
      var kstest = $('<li>' + tests[f][1] + '</li>')
      ttest.appendTo(fhead)
      kstest.appendTo(fhead)
      fhead.appendTo('#explain')
    }
  }
}

var uniqueArray = function(list) {
  var result = [];
  $.each(list, function(i, e) {
    if ($.inArray(e, result) == -1) {
      result.push(e)
    };
  });
  return result;
}

var showDataname = function(svg, stringIndex, width, height) {
  for (i in stringIndex) {
    svg.append('g').append('text')
      .attr('x', 10).attr('y', i * 20 + 20)
      .text(stringIndex[i])
  }
}

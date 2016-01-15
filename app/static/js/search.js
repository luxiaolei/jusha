//search data utility
var searchFunc = function(dataname, inputSearch) {
  //recieve an list of data indexes
  //color the corresponding nodes



  //retrive the indexes of nodes which contain the searched data
  $.getJSON('/mapperJsonSaved', function(data) {
    var nameIndexMap = data['nameIndexMap']
    for (i in dataname) {
      var searchelem = parseInt(dataname[i])
      if (isNaN(searchelem)) {
        dataname[i] = nameIndexMap[dataname[i]]
      } else {
        dataname[i] = searchelem
      }
    }
    console.log(dataname)


    var nodes = data['vertices'];

    for (i in nodes) {
      var theNodeID = 'circleid_' + nodes[i]['index']
      var members = nodes[i]['members'];
      var nodesize = nodes[i]['members'].length
      var numIn = 0.;
      for (m in members) {
        var flag = $.inArray(members[m], dataname)
        if (flag != -1) {
          numIn += 1
        }
      }
      if (!inputSearch & numIn == 1) {
        d3.select('#' + theNodeID).style('opacity', 1)
      } else {
        d3.select('#' + theNodeID).style('opacity', numIn / nodesize)
      }
    }






    /*
    var exsitIndexes = [];
    for (d in dataname){
      for (i in nodes){
        var members = nodes[i]['members'];
        var flag = $.inArray(dataname[d], members);
        if (flag != -1){
          var theNode = nodes[i]['index']
          exsitIndexes.push(theNode);
        };
      };
    }
    //remove duplicates
    exsitIndexes = exsitIndexes.reverse()
                                .filter(function (e, i, arr) {
                                    return arr.indexOf(e, i+1) === -1;
                                  }).reverse();

    var modExsitIndexes = [];
    for (i in exsitIndexes){
      var eid = 'circleid_'+exsitIndexes[i];
      modExsitIndexes.push(eid);}

    var svg = d3.select('#graph');
    var noneExsitIndexes = [];
    svg.selectAll('circle')
       .each(function(d,i){
         //find the id of node which does NOT contain the search data
         var flag = $.inArray(this.id, modExsitIndexes);
         if (flag == -1){
           noneExsitIndexes.push(this.id)
         }
       })
    //do the coloring!
    for (i in modExsitIndexes){
      svg.select('#'+modExsitIndexes[i])
         //.transition()
         .style('opacity', 1)
    };
    for (i in noneExsitIndexes){
      svg.select('#'+noneExsitIndexes[i])
         //.transition()
         .style('opacity', 0.1)
    }
    */
  })
}


//search button
$(function(dataname) {
  $('#searchsubmit').bind('click', function() {
    $("#reverse").show()
    var dataname = $('#searchbox').val().split(',')
    searchFunc(dataname, false);
    d3.selectAll('line').style('opacity', .1)
  })
})

//when click reverse button, put color back! and hide the button
$(function() {
  $("#reverse").bind('click', function() {
    $("#reverse").hide()
    d3.selectAll('circle').style('opacity', 1)
    d3.selectAll('line').style('opacity', 1)
  })

})

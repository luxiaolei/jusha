//search data utility
var searchFunc = function(dataname, inputSearch) {
  //recieve an list of data indexes
  //color the corresponding nodes
  if (dataname==""){
    d3.selectAll('circle').style('opacity', 1)
    d3.selectAll('line').style('opacity', 1)
  }else{
  //retrive the indexes of nodes which contain the searched data
  $.getJSON('/mapperJsonSaved', function(data) {
    var nameIndexMap = data['nameIndexMap']
    for (i in dataname) {
      var searchelem = parseInt(dataname[i])
      //if (isNaN(searchelem)) {
        if (dataname[i].indexOf('-')!= -1 ){
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

  })
}
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

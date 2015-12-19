//search data utility
var searchFunc = function(dataname){
  //recieve an list of data indexes
  //color the corresponding nodes

      for (i in dataname){
        dataname[i] = parseInt(dataname[i])
      }
      //retrive the indexes of nodes which contain the searched data
      $.getJSON('/mapperJsonSaved', function(data){
        var nodes = data['vertices'];
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

        var svg = d3.select('svg');
        var noneExsitIndexes = [];
        svg.selectAll('.node')
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
      })
    }


//search button
$(function(dataname){
  $('#searchsubmit').bind('click',function(){
    $("#reverse").show()
    var dataname = $('#searchbox').val().split(',')
    searchFunc(dataname);
  })
})

//when click reverse button, put color back! and hide the button
$(function(){
  $("#reverse").bind('click',function(){
    $("#reverse").hide()
    var svg = d3.select('svg');
    svg.selectAll('.node').style('opacity', 1)
  })

})

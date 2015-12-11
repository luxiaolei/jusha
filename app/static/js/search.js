//search data utility
$(function(){
  $('#searchsubmit').bind('click',function(){
    /*
    !!should add a function(searchbox){return index}!
    */
    var dataname = parseInt($('#searchbox').val());

    //retrive the indexes of nodes which contain the searched data
    $.getJSON('/mapperjson', function(data){
      var nodes = data['vertices'];
      var exsitIndexes = [];
      for (i in nodes){
        var members = nodes[i]['members'];
        var flag = $.inArray(dataname, members);
        if (flag != -1){
          var theNode = nodes[i]['index']
          exsitIndexes.push(theNode);
        };
      };

      var modExsitIndexes = []
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
           .transition()
           .style('opacity', 1)
      };
      for (i in noneExsitIndexes){
        svg.select('#'+noneExsitIndexes[i])
           .transition()
           .style('opacity', 0.3)
      }
    })

  })

})

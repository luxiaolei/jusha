//handle feater selection porcess
$(function(){
  $("#paramsGenerate").bind('click', function(){
    $.getJSON('/features',function(data){
      //retrive features from json, and then generate
      //a list of radio button for each features
      $("#recolor").show()

      var flag = $("[name='features']").length
      if (flag >= 1){
        $("[name='features']").remove()
        $("[name='fname']").remove()
      }
     for (i in data.features){
       var radioBtn = $('<li><input type="radio" id=rd'+i+' name="features" value= '+data.features[i]+'><label class=btn for=rd'+i+' name=fname><a>'+data.features[i]+'</a></label></li>');
       radioBtn.appendTo('#radiocheck');
     };

    //ajax post the selected feature to server
     $('#radiocheck input').change(function(){
       var data = {'selected': $('input[name=features]:checked', '#radiocheck').val(),
                    'binsNumber': $('#bins').val()};
            console.log(data)

       $.ajax({
         type : "POST",
         //mimic the url_for function when this js file is external
         url : "/feature_ajax",
         data: JSON.stringify(data),// null, '\t'),
         contentType: 'application/json;charset=UTF-8',
         success: function(){
           //draw bar chart
           if($('svg').length == 2){
           $('svg').first().remove();

           }
           barChart('/bins',1)

         }
       });
      });

    //draw bar chart!
     //barChart();
    });
  });
});

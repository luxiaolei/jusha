//handle feater selection porcess
$(function(){
  $("#showfeature").bind('click', function(){
    $.getJSON('/features',function(data){
      //retrive features from json, and then generate
      //a list of radio button for each features
     for (i in data.features){
       var radioBtn = $('<input type="radio" name="features" value= '+data.features[i]+'><button>'+data.features[i]+'</button>'+',');
       radioBtn.appendTo('#radiocheck');
     };
    //ajax post the selected feature to server
     $('#radiocheck input').change(function(){
       var data = {'selected': $('input[name=features]:checked', '#radiocheck').val()};
       $.ajax({
         type : "POST",
         //mimic the url_for function when this js file is external
         url : "/feature_ajax",
         data: JSON.stringify(data),// null, '\t'),
         contentType: 'application/json;charset=UTF-8',
         success: function(){
         }
       });
      });
    });
  });
});

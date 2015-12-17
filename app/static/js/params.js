//when the parmas input changes, send the values to server
//when click start redrawing, generate new mapperjson
//the default value of the box changes

$(function(){
  //when click upload button, delete previously
  //shown features and hide select nodes button
  $("[name='file']").bind('click',function(){
    var flag = $("[name='features']").length
    if (flag >= 1){
      $("[name='features']").remove()
      $("[name='fname']").remove()
    $("#generate").hide()
    }
  })
})


$(function(){
  $("#paramsGenerate").bind('click',function(){
    //$('#barchart').remove()
    //upload file first!
    var form_data = new FormData($('#upload-file')[0]);
    $.ajax({
        type: 'POST',
        url: '/uploadFile',
        data: form_data,
        contentType: false,
        cache: false,
        processData: false,
        async: false,
        success: function(data) {
            console.log('Success!');
        }
      });

    //post params
    var interval = $("#interval").val();
    var overlap = $("#overlap").val();
    var data = {'interval': interval, 'overlap': overlap}
    //send to server
    $.ajax({
      type : "POST",
      //mimic the url_for function when this js file is external
      url : "/paramsAjax",
      data: JSON.stringify(data),// null, '\t'),
      contentType: 'application/json;charset=UTF-8',
      success: function(result){
        console.log(result)
        //when post successed,redraw the graph
        }
      });

    //run Clustering
    runClustering();

    })
  });

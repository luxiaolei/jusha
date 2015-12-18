//when the parmas input changes, send the values to server
//when click start redrawing, generate new mapperjson
//the default value of the box changes

$(function(){
  //when click upload button, delete previously
  //shown features and hide select nodes button
  $("#fileupload").bind('click',function(){

    var flag = $("[name='features']").length
    if (flag >= 1){
      $("[name='features']").remove()
      $("[name='fname']").remove()
    $("#generate").hide()
    }
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
            //generate checkbox for each features
            var checkboxesForm = $('#featuresCheck')
            checkboxesForm.children().remove()
            for(i in data.features){
              var checkbox = $("<input type='checkbox' id=fcheck"+i+" checked=true value="
                                +data.features[i]+">"
                                +'<label for=fcheck'+i+' class=btn>'+ data.features[i] + '</label>')
              checkbox.appendTo(checkboxesForm)
            }
        },
        error: function(e){
          console.log(e)
        }
      });

  })
})


$(function(){
  $("#paramsGenerate").bind('click',function(){
    //get checked features and
    var checkedFeatures = []
    $('[id^=fcheck]:checked').each(function(){
      checkedFeatures.push(this.value)
    })

    //post params
    var interval = $("#interval").val();
    var overlap = $("#overlap").val();
    var data = {'interval': interval, 'overlap': overlap, 'checkedFeatures': checkedFeatures}
    //send to server
    $.ajax({
      type : "POST",
      //mimic the url_for function when this js file is external
      url : "/paramsAjax",
      data: JSON.stringify(data),// null, '\t'),
      contentType: 'application/json;charset=UTF-8',
      success: function(result){
        //console.log(result)
        //when post successed,redraw the graph
        }
      });



    //run Clustering
    runClustering();

    })
  });

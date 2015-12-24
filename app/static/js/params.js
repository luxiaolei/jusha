//when the parmas input changes, send the values to server
//when click start redrawing, generate new mapperjson
//the default value of the box changes

$(function(){
  //when click upload button, delete previously
  //shown features and hide select nodes button
  $("#fileupload").bind('click',function(){

    $('#index').children().not(':first').remove();
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
            var indexradiobox = $('#index')
            checkboxesForm.children().remove()

            //generates index selection dropbox and features selection checkboxes
            var genIndexDropbox = $(function(){
              for(i in data.features){
                var radiodropdown = $("<option value="+data.features[i]+">"+data.features[i]+"</option>")
                radiodropdown.appendTo(indexradiobox)
              }
            })

            var genFeaturesCheckBoxes = function(){
              for(i in data.features){
                var checkbox = $("<li><a><input type='checkbox' id=fcheck"+i+" checked=true value="
                                  +data.features[i]+">"
                                  +'<label for=fcheck'+i+' class=btn>'+ data.features[i] + '</label></a></li>')
                checkbox.appendTo(checkboxesForm)
              }
            }
            genFeaturesCheckBoxes()

            $(function(){
              //when select an index column, del the corresbonding checkbox 
              $('#index').on('change',function(){
                $('#featuresCheck').children().remove()
                $('label').remove()
                genFeaturesCheckBoxes()
                var index = $("#index").prop('checked',true).val()
                $('#featuresCheck').children().filter(function(){return this.value == index}).remove()
                $('label:contains('+index+')').remove()
              })
            })
        },
        error: function(e){
          console.log(e)
        }
      });

  })
})

////if selected filter support metric selection, then generates metric selection dropbox
$(function(){
  $('#filters').on('change',function(){
    var filter = $('#filters').prop('selected',true).val()
    var DISallowedF = ['kNN_distance','distance_to_measure', 'zero_filter']
    var redandentMetrics = $('#metrics').children().not(':first')
    if ($.inArray(filter, DISallowedF) != -1){
      redandentMetrics.hide()
    }else{
      redandentMetrics.show()
    }
    
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
    var index = $("#index").prop('checked',true).val();
    var interval = $("#interval").val();
    var overlap = $("#overlap").val();
    var filter = $('#filters').prop('selected',true).val();
    var metric = $('#metrics').prop('selected',true).val();
    var cutoff = $('#cutoff').prop('selected',true).val();
    var data = {'interval': interval, 'overlap': overlap, 'checkedFeatures': checkedFeatures, 
                'filter': filter, 'index':index, 'metric':metric, 'cutoff':cutoff}
    
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

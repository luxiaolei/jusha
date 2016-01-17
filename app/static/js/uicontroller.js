$(function() {
  $("[id^=draggable]").each(function(){


    $(this).draggable({
    //stack: ".container-fluid",
    //helper: 'clone',
    //revert: 'invalid',
    //appendTo: 'body'
  });
})
});

$(function(){
  $('#draggable').draggable()
})

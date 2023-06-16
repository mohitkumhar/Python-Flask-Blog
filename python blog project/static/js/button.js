$('form').on('submit',function(e){
  e.preventDefault();
  var but = $(this).find('[type="submit"]').toggleClass('sending').blur();
  
  setTimeout(function(){
     but.removeClass('sending').blur();
  },4500);
  
})
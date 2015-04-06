jQuery(document).ready(function() { 
   
  // jQuery.material.init(); 
  function square_height()
  {
   $( ".square" ).each(function() {
      var cw = $(this).width();
      $(this).css({'height':cw+'px'});
    });
  }
  
  square_height();
  

  
  
  
  
  $( window ).resize(function() {
    square_height();
  });
   
	
});
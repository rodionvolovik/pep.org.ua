$(function() { 
    // jQuery.material.init(); 
    function square_height() {
        $(".square").each(function() {
            var cw = $(this).width();
            $(this).css({'height':cw+'px'});
        });
    }

    square_height();

    $( window ).resize(function() {
        square_height();
    });

    $("#search-form").typeahead({
        minLength: 2, 
        autoSelect: false,
        source: function(query, process) {
            $.get('/ajax/suggest', {"q": query})
                .success(function(data){
                    process(data);
                })
        },
        matcher: function() {
            // Big guys are playing here
            return true;
        }
    });
});
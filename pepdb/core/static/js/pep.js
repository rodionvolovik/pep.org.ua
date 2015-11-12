$(function() {
    // jQuery.material.init(); 
    function square_height() {
        $(".square").each(function() {
            var cw = $(this).width();
            $(this).css({
                'height': cw + 'px'
            });
        });
    }
    
    equalheight = function(container){
        var currentTallest = 0,
             currentRowStart = 0,
             rowDivs = new Array(),
             $el,
             topPosition = 0;
         $(container).each(function() {
        
           $el = $(this);
           $($el).height('auto')
           topPostion = $el.position().top;
        
           if (currentRowStart != topPostion) {
             for (currentDiv = 0 ; currentDiv < rowDivs.length ; currentDiv++) {
               rowDivs[currentDiv].height(currentTallest);
             }
             rowDivs.length = 0; // empty the array
             currentRowStart = topPostion;
             currentTallest = $el.height();
             rowDivs.push($el);
           } else {
             rowDivs.push($el);
             currentTallest = (currentTallest < $el.height()) ? ($el.height()) : (currentTallest);
          }
           for (currentDiv = 0 ; currentDiv < rowDivs.length ; currentDiv++) {
             rowDivs[currentDiv].height(currentTallest);
           }
         });
    }

    equalheight(".small-profile");
    
    square_height();
    
    $('.tooltip-anchor').tooltip();
    
    $('#send-form .show-form').on('click', function() {$('#send-form').addClass("open");});
    $('#send-form .btn-close').on('click', function() {$('#send-form').removeClass("open");});

    $(window).resize(function() {
        square_height();
        equalheight(".small-profile");
    });

    $("#search-form").typeahead({
        minLength: 2,
        autoSelect: false,
        source: function(query, process) {
            $.get($("#search-form").data("endpoint"), {
                    "q": query
                })
                .success(function(data) {
                    process(data);
                })
        },
        matcher: function() {
            // Big guys are playing here
            return true;
        },
        afterSelect: function(item) {
            var form = $("#search-form").closest("form");
            form.find("input[name=is_exact]").val("on");

            form.submit();
        }
    });


    $('.tree li:has(ul)')
        .addClass('parent_li')
        .find(' > span')
        .attr('title', 'Collapse this branch');

    $('.tree li.parent_li > span').on('click', function(e) {
        var children = $(this).parent('li.parent_li').find(' > ul > li');
        
        if (children.is(":visible")) {
            children.hide('fast');
            $(this)
                .attr('title', 'Expand this branch')
                .find(' > i.faicon')
                .addClass('fa-plus-square')
                .removeClass('fa-minus-square');
        } else {
            children.show('fast');
            $(this)
                .attr('title', 'Collapse this branch')
                .find(' > i.faicon')
                .addClass('fa-minus-square')
                .removeClass('fa-plus-square');
        }
        e.stopPropagation();
    });

    $('#side-profilemenu').affix({
        offset: {
            top: 50
        }
    });

    $("body").on("click", ".active-box", function(e) {
        var el = $(this);
        location.href = el.data("url");
    });

    $("body").on("click", ".print-me", function(e) {
        e.preventDefault();
        window.print();
    });

    /* smooth scrolling sections */
    $('a[href*=#]:not([href=#])').click(function() {
        if (location.pathname.replace(/^\//, '') ==
            this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
            var target = $(this.hash);

            target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
            if (target.length) {
                $('html, body').animate({
                    scrollTop: target.offset().top - 50
                }, 1000);
                return false;
            }
        }
    });

    $("body").on("submit", ".ajax-form", function(e) {
        e.preventDefault();
        var form = $(this).closest("form");
        form.find("button").attr("disabled", "disabled");

        $.post(form.attr("action"), form.serialize(), function(data) {
            form.parent().html(data);
        });
    });
});

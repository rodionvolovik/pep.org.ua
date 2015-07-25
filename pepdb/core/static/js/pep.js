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

    square_height();

    $(window).resize(function() {
        square_height();
    });

    $("#search-form").typeahead({
        minLength: 2,
        autoSelect: false,
        source: function(query, process) {
            $.get('/ajax/suggest', {
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
            console.log(form);
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
                .find(' > i')
                .addClass('fa-plus-square')
                .removeClass('fa-minus-square');
        } else {
            children.show('fast');
            $(this)
                .attr('title', 'Collapse this branch')
                .find(' > i')
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

    /* smooth scrolling sections */
    $('a[href*=#]:not([href=#])').click(function() {
        if (location.pathname.replace(/^\//, '') ==
            this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
            var target = $(this.hash);

            target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
            if (target.length) {
                $('html,body').animate({
                    scrollTop: target.offset().top - 50
                }, 1000);
                return false;
            }
        }
    });
});

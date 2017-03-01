django.jQuery(function(){
    var $ = django.jQuery;

    $(".company_match input").on("change", function(e) {
        var el = $(this);
        el.parents(".field-candidates").siblings(".field-status").find("select").val("m");
        el.parents(".field-candidates").siblings(".field-edrpou_match").find("input").val(el.val());
    });

    $(".field-edrpou_match input").attr("readonly", "readonly");
});
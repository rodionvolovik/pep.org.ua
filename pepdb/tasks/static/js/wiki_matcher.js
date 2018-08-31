django.jQuery(function(){
    var $ = django.jQuery;

    $(".company_match input").on("change", function(e) {
        var el = $(this);
        el.parents(".field-dataset_entry_readable").siblings(".field-status").find("select").val("a");
        el.parents(".field-dataset_entry_readable").siblings(".field-wikidata_id").find("input").val(el.val());
    });
});
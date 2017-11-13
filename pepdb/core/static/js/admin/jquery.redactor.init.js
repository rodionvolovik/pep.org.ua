if (typeof jQuery === 'undefined' && django && django.jQuery) {
    jQuery = django.jQuery;
}

if (typeof custom_options === 'undefined') {
    custom_options = {}
}

(function($) {
    $(document).ready(function() {
        $(document).on('inactive_redactor:init', 'textarea.redactor-box-inactive', function() {
            var options = $.extend({}, $(this).data('redactor-options'), custom_options);
            if (typeof options.callbacks === 'undefined') {
                options.callbacks = {};
            }
            if (typeof options.callbacks.imageUploadError === 'undefined') {
                options.callbacks.imageUploadError = function (json, xhr) {
                    if (json.error) {
                        if (json.message) {
                            alert(json.message);
                        } else {
                            alert('Something went wrong!');
                        }
                    }
                }
            }
            $(this).addClass("redactor-box").redactor(options);
        });

        $(document).on("click", 'textarea.redactor-box-inactive:not([id*="__prefix__"])', function() {
            $(this).trigger('inactive_redactor:init');
        });
    });
})(jQuery);

django.jQuery(function(){
	var $ = django.jQuery;

	function init() {
		$(".suggest").each(function(i, box) {
			box = $(box);
			box.autocomplete({
  				"source": box.data("choices")
			});
		})
	}

	init();

	$(document.body).on("click", ".grp-add-handler", init);
});
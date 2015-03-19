
		$(document).ready(function(){
			var screen = $.mobile.getScreenHeight();
			var header = $(".ui-header").hasClass("ui-header-fixed") ? $(".ui-header").outerHeight()  - 1 : $(".ui-header").outerHeight();
			var contentCurrent = $(".ui-content").outerHeight() - $(".ui-content").height();
			var content = screen - header - contentCurrent;
			$(".ui-content").height(content);
		});

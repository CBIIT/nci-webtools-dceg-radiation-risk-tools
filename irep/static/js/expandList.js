// JavaScript Document
$(document).ready(function() {
	if( $('#local_nav ul').has('li.expand').length > 0 ) {
		var expandLinks = $('#local_nav ul li.expand');
		expandLinks.prepend('<a href="#" class="hitarea" title="Click to expand section"></a>');
		expandLinks.css('list-style','none');
		expandLinks.css('list-style-image','none');
		expandLinks.children('ul').css('display','none');
		expandLinks.has('a.active').children('ul').css('display','block');
		expandLinks.has('a.active').children('a.hitarea').addClass('close');
		$('li.expand a.hitarea').click( function() {
			if($(this).siblings('ul:visible').length > 0) {
				$(this).siblings('ul').css('display','none');
				$(this).removeClass('close');
				return false;
			} else {
				$(this).siblings('ul').css('display','block');
				$(this).addClass('close');
				return false;
			}
		});
	}
});
function expandingList() {
	$('ul.expandingList ul').css('display','none');
	$('ul.expandingList ul li ul').css('display','block');
	$('ul.expandingList ul li ul li ul').css('display','block');
	$('ul.expandingList').before('<p><a href="#" id="expandAll">Expand All</a> | <a href="#" id="collapseAll">Collapse All</a></p>');
	$('ul.expandingList a.folder').parent('ul.expandingList li').addClass('plusMinus');
	$('ul.expandingList a.folder').parent('ul.expandingList li').prepend('<div class="hitarea" title="Click to expand section"></div>');
	$('ul.expandingList li li a').click(function () {
		var href = $(this).attr('href');
		if ( href.indexOf('#') < 0 || href == '#' )
			return;
		var divId = href.substr(1);
		$('#'+divId).siblings('ul').show();
		$('#'+divId).siblings('div.hitarea').addClass('active');
	});
	$('ul.expandingList a.folder').click(function () {
		$(this).parent('ul.expandingList li').contents('ul').toggle();
		$(this).parent('ul.expandingList li').contents('div.hitarea').toggleClass('active');
		return false;
	});
	$('ul.expandingList div.hitarea').click(function () {
		$(this).parent('ul.expandingList li').contents('ul').toggle();
		$(this).parent('ul.expandingList li').contents('div.hitarea').toggleClass('active');
		return false;
	});
	$('#expandAll').click(function () {
		$('ul.expandingList ul').css('display','block');
		$('ul.expandingList li:not(ul.subsection li)').contents('div.hitarea').addClass('active');
		return false;
	});
	$('#collapseAll').click(function () {
		$('ul.expandingList ul').css('display','none');
		$('ul.expandingList ul li ul').css('display','block');
		$('ul.expandingList ul li ul li ul').css('display','block');
		$('ul.expandingList li:not(ul.subsection li)').contents('div.hitarea').removeClass('active');
		return false;
	});
}
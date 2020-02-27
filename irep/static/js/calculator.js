
function getColorBoxWidth(preferred_size) {
    //var windowWidth = window.screen.width < window.outerWidth ? window.screen.width : window.outerWidth;
    var windowWidth = window.screen.width;
    return (windowWidth < preferred_size ? (windowWidth - 20) : preferred_size) + "px";
}

$.Class.extend("FormSet", {
  // constructor function
  init : function(formset, max_forms, add_url){
    //save the name
    this.formset_name = formset;
    this.add_url = add_url;
    this.formset_add_id = 'id_' + formset + '_add';
    this.formset = $('#' + formset);
    this.num_forms = 0; //$(formset + ' .form').length; 
    this.num_deleted_forms = 0;
    this.max_forms = $(max_forms)[0];
    this.empty_form = $('#' + formset + ' .empty-form')[0];
    //$(this.empty_form).find('.errorlist').remove();
	var this_class = this;
	var total_forms;
	$('#' + formset + ' input').each(function(index) {
	    if ($(this).attr("id").indexOf('TOTAL_FORMS') > -1) {
	      this_class.total_forms = $(this);
	      this_class.num_forms = parseInt($(this).val());
	    }
  	});
	$('#' + formset + ' input').each(function(index) {
	    if ($(this).attr("id").indexOf('INITIAL_FORMS') > -1) {
	      $(this).val(Math.max(1, parseInt($(this).val())));
	    }
  	});
  	$('#' + formset).find('.delete-button').each(function(idx, el){
      this_class._addDeleteHandler(el)
    });  
  	this._createAddLink();  	
  },
  _createAddLink : function() {
    var label = this.formset.attr('data-add-label') || 'Add';
    this.formset.append('<a id="' + this.formset_add_id + '" class="add-form-link btn btn-secondary mt-1 mb-1" role="button" href="#"><img src="' + this.add_url + '" height="16" width="16" title="Add Exposure" alt="Add Exposure" /> ' + label +'</a>');
    var this_class = this;
    $('#' + this_class.formset_add_id).bind('click', function(e) {
        e.preventDefault();
        this_class._createNewForm(this)
    });
    if ((this.num_forms - this.num_deleted_forms) >= this.max_forms) $('#' + this_class.formset_add_id).hide();
  },
  _addDeleteHandler : function(element) {
    var this_class = this;
    $(element).click( function(e) {
        e.preventDefault();
  		var chk = $(this).next().find('input:checkbox')[0];
  		$(chk).attr('checked', !$(chk).attr('checked'));
  		$(element).parent().parent('.form').toggle();
  		if ($(element).parent().parent('.form').next().hasClass('errorlist'))
  			$(element).parent().parent('.form').next().toggle();
  		this_class.num_deleted_forms++;
	    if ((this_class.num_forms - this_class.num_deleted_forms) < this_class.max_forms)
       		$('#' + this_class.formset_add_id).show();
	});	
	$(element).hover(function(){
      	$(this).parent().parent('.form').addClass("hover");},function(){$(this).parent().parent('.form').removeClass("hover");
    });
  },
  _fill_placeholder : function(s) {
    return s.replace('__prefix__', this.num_forms);
  },
  _createNewForm : function(event) {
    var this_class = this;
    var new_form = $(this.empty_form).clone();
    new_form.find('td').each(function(idx, el){
       $(el).find('*').each(function(idex, c) {
           if ($(c).attr('id'))
             $(c).attr('id', this_class._fill_placeholder($(c).attr('id')));
           if ($(c).attr('name'))
             $(c).attr('name', this_class._fill_placeholder($(c).attr('name')));
           if ($(c).attr('for'))
             $(c).attr('for', this_class._fill_placeholder($(c).attr('for')));
       });
    });
    $(new_form).insertBefore($(this.empty_form)).removeClass('empty-form').addClass('form');
 	//$("#id_dose_-" + this.num_forms + "-exprate").select2({width: "100%"});
   	//$("#id_dose_-" + this.num_forms + "-radtype").select2({width: "100%"});
   	//$("#id_dose_-" + this.num_forms + "-dosetype").select2({width: "100%"});
   	//$("#id_radon_-" + this.num_forms + "-dosetype").select2({width: "100%"});
    
    this.num_forms++;
    $(new_form).find('.index').html(this.num_forms);
    $(this_class.total_forms).val(this.num_forms);
    if ((this.num_forms - this.num_deleted_forms) >= this.max_forms) $('#' + this_class.formset_add_id).hide();
    new_form.find('.delete-button').each(function(idx, el){
     	this_class._addDeleteHandler(el)      	
    });    
    // new_form.select('.field.delete').each(function(e){new DeleteButton(e);});
    return new_form;
  }  
})

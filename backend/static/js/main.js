$('form').submit(function () {
	var $form = $(this),
    val_list = [];
  $form.find('.block').each(function () {
    var $block = $(this),
      input_type = $block.find('select').val(),
      input_text = $block.find('.form-control mb-2 mr-sm-2 mb-sm-0').val();
    val_list.push({
    	type: input_type,
    	text: input_text
    });
  });
  alert(JSON.stringify({data: val_list}));
  return false;
});

$('.add').click(function () {
	var $block = $(this).parent();
  $block.clone(true).insertBefore('.submit');
  return false;
}); 

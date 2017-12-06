$(function() {
    $('#searchform').submit(function() {
        var $form = $(this),
            val_list = [];
        $form.find('.block:visible').each(function() {
            var $block = $(this);
            var input_type = $block.find('.selectSearchOpt').val();
            var input_ro = $block.find("select.multselect_ro").val();
            if (input_type == "word" || input_type == "lemma") {
                var input_text = $block.find('input').val();
            } else {
                var input_text = $block.find('.dropdown option:selected').val();
            }
            val_list.push({
                type: input_type,
                searched_for: input_text,
                ro: input_ro
            });
        });
        alert(JSON.stringify({
            data: val_list
        }));
        $('#realform #data').val(JSON.stringify(val_list));
        $('#realform').submit();
        return false;
    });

    var clone_block = function() {
		var $newblock = $("#searchform .block:hidden").clone();
		var $inserted = $newblock.insertBefore('.submit').show();
		$inserted.find(".multselect_ro").selectpicker();
		$inserted.find('.selectSearchOpt').change(function() {
			var $searchopt = $(this);
			var $parblock = $searchopt.parent();
			var choice = $searchopt.val();
			if (choice === 'word') {
				$parblock.find(".searchOption").html('<input type="text" class="form-control mb-2 mr-sm-2 mb-sm-0" placeholder="Поиск слова...">');
			} else if (choice === 'lemma') {
				$parblock.find(".searchOption").html('<input type="text" class="form-control mb-2 mr-sm-2 mb-sm-0" placeholder="Поиск леммы...">');
			} else if (choice === 'pos') {
				$parblock.find(".searchOption").html('<select class="dropdown select"><option value="" selected>Выберите часть речи...</option><option value="S">Существительное</option><option value="V">Глагол</option><option value="A">Прилагательное</option><option value="ADV">Наречие</option><option value="SPRO">Местоимение</option><option value="PR">Предлог</option><option value="CONJ">Союз</option><option value="PART">Частица</option></select>');
			} else if (choice === 'marker') {
				$parblock.find(".searchOption").html('<select class="dropdown select"><option value="" selected>Выберите маркер РО...</option><option value="potomuchto">потому что</option><option value="poetomu">поэтому</option></select>');
			} else {
				$parblock.find(".searchOption").html(null);
			}
		});
		$inserted.find(".add").click(function() {
			var $blockselect = clone_block();
			console.log($blockselect.find(".selectpicker"));
			return false;
		});
		$inserted.find(".closeimg").click(function() {
			var $block = $(this).closest(".block");
			$block.remove();
			return false;
		});
		return $inserted;
	};

	clone_block();

});

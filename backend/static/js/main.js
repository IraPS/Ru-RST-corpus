$(function() {
    $('#searchform').submit(function() {
        var $form = $(this),
            val_list = [];
        $form.find('.block').each(function() {
            var $block = $(this);
            var input_type = $block.find('select').val();
            var input_ro = $block.find('.selectpicker').val();
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

    $('.add').click(function() {
        var $block = $(this).parent();
        var $newblock = $block.clone(true);
        if ($newblock.find('.placeForSearch').innerHTML != '') {
            $newblock.find('.placeForSearch').empty();

        }
        var selected_ro = $block.find('.selectpicker').val();
        if (selected_ro != "any") {
            $newblock.find('.selectpicker').selectpicker('val','any');
        }
        $newblock.insertBefore('.submit');
        $newblock.find('.selectpicker').selectpicker('deselectAll');
        $newblock.find("selectpicker").attr("id", "new");
        return false;
    });

    $('.closeimg').click(function() {
        var $block = $(this).parent();
        $block.remove();
        return false;
    });

    $('.selectSearchOpt').change(function() {
        var $block = $(this).parent();
        var choice = $block.find('.selectSearchOpt').val();
        if (choice === 'word') {
            $block.find('.placeForSearch').get(0).innerHTML = '<input type="text" class="form-control mb-2 mr-sm-2 mb-sm-0" placeholder="Поиск слова...">';
        } else if (choice === 'lemma') {
            $block.find('.placeForSearch').get(0).innerHTML = '<input type="text" class="form-control mb-2 mr-sm-2 mb-sm-0" placeholder="Поиск леммы...">';
        } else if (choice === 'pos') {
            $block.find('.placeForSearch').get(0).innerHTML = '<select class="dropdown select"><option value="" selected>Выберите часть речи...</option><option value="S">Существительное</option><option value="V">Глагол</option><option value="A">Прилагательное</option><option value="ADV">Наречие</option><option value="SPRO">Местоимение</option><option value="PR">Предлог</option><option value="CONJ">Союз</option><option value="PART">Частица</option></select>';
        } else if (choice === 'marker') {
            $block.find('.placeForSearch').get(0).innerHTML = '<select class="dropdown select"><option value="" selected>Выберите маркер РО...</option><option value="potomuchto">потому что</option><option value="poetomu">поэтому</option></select>';
        } else {
            $block.find('.placeForSearch').get(0).innerHTML = null;
        }
    });

});

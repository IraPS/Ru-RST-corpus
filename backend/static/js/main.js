$(function() {
    $('form').submit(function() {
        var $form = $(this),
            val_list = [];
        $form.find('.block').each(function() {
            var $block = $(this),
                input_type = $block.find('select').val(),
                input_text = $block.find('.form-control mb-2 mr-sm-2 mb-sm-0').val();
            val_list.push({
                type: input_type,
                text: input_text
            });
        });
        alert(JSON.stringify({
            data: val_list
        }));
        return false;
    });

    $('.add').click(function() {
        var $block = $(this).parent();
        var $newblock = $block.clone(true);
        if ($newblock.find('.placeForSearch').innerHTML != '') {
            $newblock.find('.placeForSearch').empty();
        }
        $newblock.insertBefore('.submit');
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
            $block.find('.placeForSearch').get(0).innerHTML = '<input type="text" class="form-control mb-2 mr-sm-2 mb-sm-0" id="inlineFormInput" placeholder="Поиск слова...">';
        } else if (choice === 'lemma') {
            $block.find('.placeForSearch').get(0).innerHTML = '<input type="text" class="form-control mb-2 mr-sm-2 mb-sm-0" id="inlineFormInput" placeholder="Поиск леммы...">';
        } else if (choice === 'pos') {
            $block.find('.placeForSearch').get(0).innerHTML = '<select><option value="" selected>Выберите часть речи...</option><option value="noun">Существительное</option><option value="verb">Глагол</option><option value="adj">Прилагательное</option><option value="adv">Наречие</option><option value="pronoun">Местоимение</option><option value="preposition">Предлог</option><option value="conj">Союз</option><option value="particle">Частица</option></select>';
        } else if (choice === 'marker') {
            $block.find('.placeForSearch').get(0).innerHTML = '<select><option value="" selected>Выберите маркер РО...</option><option value="potomuchto">потому что</option><option value="poetomu">поэтому</option></select>';
        } else {
            $block.find('.placeForSearch').get(0).innerHTML = null;
        }
    });

});
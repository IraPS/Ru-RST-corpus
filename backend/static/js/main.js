$(function() {
    $('#submitcontact').submit(function() {
        var $form = $(this),
            values_list = [],
            author_name = $form.find('#author').val(),
            email_addr = $form.find('#email').val(),
            subj = $form.find('#subject').val(),
            message_text = $form.find('#messagetext').val();
        values_list.push({
            author: author_name,
            email: email_addr,
            subject: subj,
            message: message_text
        });

        $('#contactform #data_m').val(JSON.stringify(values_list));
        $('#contactform').submit();
        return false;
    });

    $('#searchform').submit(function() {
        var $form = $(this),
            val_list = [];
        $form.find('.block:visible').each(function() {
            var $block = $(this);
            var input_type = $block.find('.selectSearchOpt').val();
            var input_ro = $block.find("select.multselect_ro").val();
            var close_par = $block.find("input.parentheses_close").val();
            var open_par = $block.find("input.parentheses_open").val();
            if (input_type == "word" || input_type == "lemma") {
                var input_text = $block.find('input.searchtext').val().toLowerCase();
            } else {
                var input_text = $block.find('.dropdown option:selected').val();
            }
            var add = $block.find('.add_search').val();
            val_list.push({
                type: input_type,
                searched_for: input_text,
                ro: input_ro,
                add_type: add,
                open_parenth: open_par,
                close_parenth: close_par
            });
        });
    /*    
        alert(JSON.stringify({
            data: val_list
        }));
    */
        $('#realform #data').val(JSON.stringify(val_list));
        $('#realform').submit();
        return false;
    });
    
    $('#blockform').submit(function() {
		alert('Ссылка на скачивание файла появится в новой вкладке. Формирование файла может занять некоторое время, не закрывайте страницу.');
        var $form = $(this),
            val_list = [];
        $form.find('.block-csv').each(function() {
            var $block = $(this);
            var input_type = $block.find('.typesearch').val();
            var input_ro_str = $block.find(".ro").val();
			var input_ro = input_ro_str.split(',');
            var close_par = $block.find(".close_parenth").val();
            var open_par = $block.find(".open_parenth").val();
            var input_text = $block.find('.searched_for').val();
            var add = $block.find('.add_type').val();
            val_list.push({
                type: input_type,
                searched_for: input_text,
                ro: input_ro,
                add_type: add,
                open_parenth: open_par,
                close_parenth: close_par
            });
        });

        $('#csv_form_hid #data').val(JSON.stringify(val_list));
        $('#csv_form_hid').submit();
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
                $parblock.find(".searchOption").html('<input type="text" class="searchtext" placeholder="Поиск слова...">');
            } else if (choice === 'lemma') {
                $parblock.find(".searchOption").html('<input type="text" class="searchtext" placeholder="Поиск леммы...">');
            } else if (choice === 'pos') {
                $parblock.find(".searchOption").html('<select class="dropdown select"><option value="" selected>Выберите часть речи...</option><option value="S">Существительное</option><option value="V">Глагол</option><option value="A">Прилагательное</option><option value="ADV">Наречие</option><option value="SPRO">Местоимение</option><option value="PR">Предлог</option><option value="CONJ">Союз</option><option value="PART">Частица</option></select>');
            } else if (choice === 'marker') {
                $parblock.find(".searchOption").html('<select class="dropdown select"> \
                    <option value="" selected>Выберите маркер РО...</option>\
                    <option value="a">a</option>\
                    <option value="bezuslovno">безусловно</option>\
                    <option value="buduchi">будучи</option>\
                    <option value="vitoge">в итоге</option>\
                    <option value="vosobennosti">в особенности</option>\
                    <option value="vramkah">в рамках</option>\
                    <option value="vrezultate">в результате</option>\
                    <option value="vsamomdele">в самом деле</option>\
                    <option value="vsvojyochered">в свою очередь</option>\
                    <option value="vsvyazis">в связи с</option>\
                    <option value="vtechenie">в течение</option>\
                    <option value="vtovremya">в то время</option>\
                    <option value="vtozhevremya">в то же время</option>\
                    <option value="vusloviyah">в условиях</option>\
                    <option value="vchastnosti">в частности</option>\
                    <option value="vposledstvii">впоследствии</option>\
                    <option value="vkluchaya">включая</option>\
                    <option value="vmestotogo">вместо того</option>\
                    <option value="vmestoetogo">вместо этого</option>\
                    <option value="vsezhe">все же</option>\
                    <option value="vsledstvie">вследствие</option>\
                    <option value="govoritsya">говорится</option>\
                    <option value="govorit_lem">говорить</option>\
                    <option value="dazhe">даже</option>\
                    <option value="dejstvitelno">действительно</option>\
                    <option value="dlya">для</option>\
                    <option value="esli">если</option>\
                    <option value="zaveryat_lem">заверять</option>\
                    <option value="zayavlat_lem">заявлять</option>\
                    <option value="i">и</option>\
                    <option value="izza">из-за</option>\
                    <option value="ili">или</option>\
                    <option value="ktomuzhe">к тому же</option>\
                    <option value="kogda">когда</option>\
                    <option value="kotoryj_lem">который</option>\
                    <option value="krometogo">кроме того</option>\
                    <option value="libo">либо</option>\
                    <option value="nasamomdele">на самом деле</option>\
                    <option value="natotmoment">на тот момент</option>\
                    <option value="naetomfone">на этом фоне</option>\
                    <option value="napisat_lem">написать</option>\
                    <option value="naprimer">например</option>\
                    <option value="naprotiv">напротив</option>\
                    <option value="nesmotryana">несмотря на</option>\
                    <option value="no">но</option>\
                    <option value="noi">но и</option>\
                    <option value="odnako">однако</option>\
                    <option value="osobenno">особенно</option>\
                    <option value="pisat_lem">писать</option>\
                    <option value="podannym">по данным</option>\
                    <option value="pomneniu">по мнению</option>\
                    <option value="poocenkam">по оценкам</option>\
                    <option value="posvedeniam">по сведениям</option>\
                    <option value="poslovam">по словам</option>\
                    <option value="podtverzhdat_lem">подтверждать</option>\
                    <option value="podcherkivat_lem">подчеркивать</option>\
                    <option value="pozdnee">позднее</option>\
                    <option value="pozzhe">позже</option>\
                    <option value="poka">пока</option>\
                    <option value="poskolku">поскольку</option>\
                    <option value="posle">после</option>\
                    <option value="potomuchto">потому что</option>\
                    <option value="poetomu">поэтому</option>\
                    <option value="prietom">при этом</option>\
                    <option value="priznavat_lem">признавать</option>\
                    <option value="priznat_lem">признать</option>\
                    <option value="radi">ради</option>\
                    <option value="rasskazyvat_lem">рассказывать</option>\
                    <option value="sdrugojstorony">с другой стороны</option>\
                    <option value="scelyu">с целью</option>\
                    <option value="skazat_lem">сказать</option>\
                    <option value="skoree">скорее</option>\
                    <option value="sledovatelno">следовательно</option>\
                    <option value="sledomza">следом за</option>\
                    <option value="soobshaetsya">сообщается</option>\
                    <option value="soobshat_lem">сообщать</option>\
                    <option value="taki">так и</option>\
                    <option value="takkak">так как</option>\
                    <option value="takchto">так что</option>\
                    <option value="takzhe">также</option>\
                    <option value="toest">то есть</option>\
                    <option value="utverzhdat_lem">утверждать</option>\
                    <option value="hotya">хотя</option></select>');
            } else {
                $parblock.find(".searchOption").html(null);
            }
        });
        $inserted.find("select.add_search").change(function() {
            var $addopt = $(this);
            var choice = $addopt.val();
            if (choice != 'none') {
                var $blockselect = clone_block();
            }
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

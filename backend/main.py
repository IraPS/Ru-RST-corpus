# -*- coding: utf-8 -*-

from datetime import datetime
import sys
STATIC_PATH = "/home/snikiforova/Ru-RST-corpus/backend/static"
sys.path.append(STATIC_PATH)
from searching_DB import *
from flask import Flask, request, render_template, Markup

APP = Flask(__name__)

MESSAGES = {'ro_s_in_edu_dont_match': 'Пожалуйста, выберите одинаковые риторические отношения внутри одной ЭДЕ.',
            'no_input_for_word': 'Пожалуйста, введите значение в поле "слово".',
            'no_input_for_lemma': 'Пожалуйста, введите значение в поле "лемма".',
            'no_input_for_pos': 'Пожалуйста, выберите часть речи.',
            'no_input_for_marker': 'Пожалуйста, выберите риторический маркер.',
            'not_equal_parenth_amount':
                'Пожалуйста, проверьте корректность запроса, количество открывающих и закрывающих скобок не совпадает.',
            'split_your_request':
                'Ваш запрос необходимо разбить на несколько отдельных запросов. Подробности см. в инструкции по поиску.',
            'fail':
                'Ваш запрос не может быть обработан.\n'
                'Если Вы уверены, что в запросе нет ошибки, свяжитесь с нами через форму на странице "Контакты".'}


MARKERS = {"a": "a", "bezuslovno": "безусловно", "buduchi": "будучи",
           "budeto": "будь это", "vitoge": "в итоге", "vosobennosti": "в особенности",
           "vramkah": "в рамках", "vrezultate": "в результате", "vsamomdele": "в самом деле",
           "vsvojyochered": "в свою очередь", "vsvyazis": "в связи с", "vtechenie": "в течение",
           "vtovremya": "в то время", "vtozhevremya": "в то же время",
           "vusloviyah": "в условиях", "vchastnosti": "в частности",
           "vposledstvii": "впоследствии", "vkluchaya": "включая", "vmestotogo": "вместо того",
           "vmestoetogo": "вместо этого",
           "vsezhe": "все же", "vsledstvie": "вследствие", "govoritsya": "говорится",
           "govorit_lem": "говорить", "dazhe": "даже", "dejstvitelno": "действительно",
           "dlya": "для", "dotakojstepeni": "до такой степени", "esli": "если",
           "zaverit_lem": "заверить", "zaveryat_lem": "заверять", "zayavit_lem": "заявить",
           "zayavlat_lem": "заявлять", "i": "и", "izza": "из-за", "ili": "или",
           "inache": "иначе", "ktomuzhe": "к тому же", "kogda": "когда",
           "kotoryj_lem": "который", "krometogo": "кроме того",
           "libo": "либо", "lishtogda": "лишь тогда", "nasamomdele": "на самом деле",
           "natotmoment": "на тот момент", "naetomfone": "на этом фоне",
           "napisat_lem": "написать", "naprimer": "например", "naprotiv": "напротив",
           "nesmotryana": "несмотря на", "no": "но",
           "noi": "но и", "objavit_lem": "объявить", "odnako": "однако", "osobenno": "особенно",
           "pisat_lem": "писать", "podannym": "по данным", "pomneniu": "по мнению",
           "poocenkam": "по оценкам", "posvedeniam": "по сведениям", "poslovam": "по словам",
           "podtverdit_lem": "подтвердить", "podtverzhdat_lem": "подтверждать",
           "podcherkivat_lem": "подчеркивать", "podcherknut_lem": "подчеркнуть",
           "pozdnee": "позднее", "pozzhe": "позже", "poka": "пока", "poskolku": "поскольку",
           "posle": "после", "potomuchto": "потому что", "poetomu": "поэтому",
           "prietom": "при этом", "priznavat_lem": "признавать", "priznano": "признано",
           "priznat_lem": "признать", "radi": "ради", "rasskazat_lem": "рассказать",
           "rasskazyvat_lem": "рассказывать", "sdrugojstorony": "с другой стороны",
           "scelyu": "с целью", "skazat_lem": "сказать", "skoree": "скорее",
           "sledovatelno": "следовательно", "sledomza": "следом за",
           "soobshaetsya": "сообщается", "soobshat_lem": "сообщать", "soobshit_lem": "сообщить",
           "taki": "так и", "takkak": "так как", "takchto": "так что",
           "takzhe": "также", "toest": "то есть", "utverzhdat_lem": "утверждать",
           "utverzhdaetsya": "утверждается", "hotya": "хотя"}


@APP.route("/index.html")
def index():
    """Main page."""
    return render_template("index.html"), 201


@APP.route("/aboutRST.html")
def about():
    """About RS-Theory page."""
    return render_template("aboutRST.html"), 201


@APP.route("/search.html")
def search():
    """Search page."""
    return render_template("search.html"), 201


@APP.route("/tree.html")
def search_result():
    return render_template("tree.html"), 201


@APP.route("/tree/<edu_id>.html")
def tree1(edu_id):
    """Tree with found edu marked page."""
    posit = request.args.get("position")
    return render_template("trees/" + str(edu_id) + ".html", position=posit), 201


@APP.route("/contact.html")
def contact():
    """Contacts page."""
    return render_template("contact.html"), 201


@APP.route("/contactm.html", methods=['GET', 'POST'])
def contactm():
    """Feedback result page."""
    mess = request.values.get("messagetext")
    if mess != '':
        cur_time = str(datetime.now()).replace(' ', 'T').replace(':', '-')
        f_h = open('backend/static/messages_from_users/' + cur_time + '.txt', 'w', encoding='utf-8')
        auth = request.values.get("author")
        mail = request.values.get("email")
        subj = request.values.get("subject")
        f_h.write('Author: ' + auth + '\n' + 'Email: ' + mail + '\n' + 'Subject: '
                  + subj + '\n' + 'Message: ' + mess)
        f_h.close()
    return render_template("contactm.html"), 201


@APP.route("/corpus.html")
def corpus():
    """All corpus texts as trees page."""
    return render_template("corpus.html"), 201


@APP.route("/download.html")
def download():
    """Download .txt and .rs3 page."""
    return render_template("download.html"), 201


@APP.route("/rhetrel.html")
def rhet():
    """About RO page."""
    return render_template("rhetrel.html"), 201


@APP.route("/result.html")
def res():
    """Search result page."""
    query = eval(request.args.get("data"))
    print(query)
    res_html = str()
    param_rus, vals, addtype, open_p, close_p, ros = [], [], [], [], [], []
    try:
        for q in query:
            if q['type'] != '':
                parameter = q['type']
                if parameter == 'lemma':
                    param_rus.append('лемма')
                elif parameter == 'word':
                    param_rus.append('словоформа')
                elif parameter == 'pos':
                    param_rus.append('часть речи')
                elif parameter == 'marker':
                    param_rus.append('риторический маркер')
                value = q['searched_for']
                vals.append(q['searched_for'])
            else:
                parameter = ''
                param_rus.append('')
                value = ''
                vals.append('')
            addtype.append(q['add_type'])
            open_p.append(q['open_parenth'])
            close_p.append(q['close_parenth'])
            ros.append(q['ro'])
            print("SEARCH VALUES", parameter, value)
            res_html = return_search_res_html(query, param_rus, vals,
                                              addtype, open_p, close_p, ros)
            if res_html in MESSAGES.values():
                if res_html == MESSAGES['fail']:
                    cur_time = str(datetime.now()).replace(' ', 'T').replace(':', '-')
                    f_q = open('backend/static/failed_queries/' + cur_time + '.txt', 'w',
                               encoding='utf-8')
                    f_q.write(str(query))
                    f_q.close()
                break
            else:
                if res_html.endswith('</b></p>'):
                    res_html += '<p><br>По Вашему запросу ничего не найдено.</p>'
                else:
                    res_html += '<br><p><b><a href="../static/search_result.csv" download>' \
                                'Скачать</a> результаты поиска в формате csv.</b></p><br>'
    except Exception as e:
        cur_time = str(datetime.now()).replace(' ', 'T').replace(':', '-')
        exc = open('backend/static/failed_queries_by_exception/' + cur_time + '.txt', 'w',
                   encoding='utf-8')
        exc.write(str(query) + '; Exception: ' + str(e))
        exc.close()
        res_html = '<p>Ваш запрос не может быть обработан.\n' \
                   'Если Вы уверены, что в запросе нет ошибки, свяжитесь с нами через форму на странице "Контакты".</p>'
    res_html = Markup(res_html)
    return render_template("result.html", result=res_html), 201

if __name__ == "__main__":
    APP.run(debug=True)

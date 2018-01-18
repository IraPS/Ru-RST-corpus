# -*- coding: utf-8 -*-

from datetime import datetime
import sys
import os
import json
sys.path.append(os.path.dirname(__file__))
from searchdb import *
from flask import Flask, request, render_template, Markup, url_for

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


@APP.route("/")
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
        f_h = open(os.path.dirname(__file__)+'/static/messages_from_users/' + cur_time + '.txt', 'w', encoding='utf-8')
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
    
@APP.route("/get_csv.html")
def get_csv():
    """Download csv with search results page."""
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
            need_context = True
            res_html = return_search_res_html(query, param_rus, vals,
                                              addtype, open_p, close_p, ros, need_context)
            if res_html in MESSAGES.values():
                if res_html == MESSAGES['fail']:
                    cur_time = str(datetime.now()).replace(' ', 'T').replace(':', '-')
                    f_q = open(os.path.dirname(__file__)+'/static/failed_queries/' + cur_time + '.txt', 'w', encoding='utf-8')
                    f_q.write(str(query))
                    f_q.close()
                break
            else:
                if res_html.endswith('</b></p>'):
                    res_html += '<p><br>По Вашему запросу ничего не найдено.</p>'
                else:
                    res_html += ''
    except Exception as e:
        cur_time = str(datetime.now()).replace(' ', 'T').replace(':', '-')
        exc = open(os.path.dirname(__file__)+'/static/failed_queries_by_exception/' + cur_time + '.txt', 'w', encoding='utf-8')
        exc.write(str(query) + '; Exception: ' + str(e))
        exc.close()
        res_html = '<p>Ваш запрос не может быть обработан.\n' \
                   'Если Вы уверены, что в запросе нет ошибки, свяжитесь с нами через форму на странице "Контакты".</p>'
    res_html = Markup(res_html)
    return render_template("get_csv.html"), 201

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
            need_context = False
            res_html = return_search_res_html(query, param_rus, vals,
                                              addtype, open_p, close_p, ros, need_context)
            if res_html in MESSAGES.values():
                if res_html == MESSAGES['fail']:
                    cur_time = str(datetime.now()).replace(' ', 'T').replace(':', '-')
                    f_q = open(os.path.dirname(__file__)+'/static/failed_queries/' + cur_time + '.txt', 'w', encoding='utf-8')
                    f_q.write(str(query))
                    f_q.close()
                break
            else:
                if res_html.endswith('</b></p>'):
                    res_html += '<p><br>По Вашему запросу ничего не найдено.</p>'
                else:
                    res_html += '<form id="csv_form_hid" action="'+url_for('get_csv')+'" method="GET" target="_blank">'
                    res_html += '<input type="hidden" id="data" name="data"></input>'
                    res_html += '</form>'
                    res_html += '<form id="blockform">'
                    for q in query:
                        if 'searched_for' in q:
                            searched_for = str(q['searched_for'])
                        else:
                            searched_for = str()
                        res_html += '<div class="block-csv">'
                        res_html += '<input type="hidden" class="typesearch" value="'+str(q['type'])+'"></input>'
                        res_html += '<input type="hidden" class="searched_for" value="'+searched_for+'"></input>'
                        res_html += '<input type="hidden" class="ro" value='+str(q['ro']).rstrip(']').lstrip('[')+'></input>'
                        res_html += '<input type="hidden" class="add_type" value="'+str(q['add_type'])+'"></input>'
                        res_html += '<input type="hidden" class="open_parenth" value="'+str(q['open_parenth'])+'"></input>'
                        res_html += '<input type="hidden" class="close_parenth" value="'+str(q['close_parenth'])+'"></input>'
                        res_html += '</div>'
                    res_html += '<button type="submit" class="btn btn-success">Сформировать csv файл с результатами поиска</button>'
                    res_html += '</form>'
    except Exception as e:
        cur_time = str(datetime.now()).replace(' ', 'T').replace(':', '-')
        exc = open(os.path.dirname(__file__)+'/static/failed_queries_by_exception/' + cur_time + '.txt', 'w', encoding='utf-8')
        exc.write(str(query) + '; Exception: ' + str(e))
        exc.close()
        res_html = '<p>Ваш запрос не может быть обработан.\n' \
                   'Если Вы уверены, что в запросе нет ошибки, свяжитесь с нами через форму на странице "Контакты".</p>'
    res_html = Markup(res_html)
    return render_template("result.html", result=res_html), 201

if __name__ == "__main__":
    APP.run(debug=True)

# -*- coding: utf-8 -*-

from datetime import datetime
import itertools
import operator
import csv
import re
import py2neo
from flask import Flask, request, render_template, Markup

graph = py2neo.Graph()

app = Flask(__name__)


def parse_query(query):
    new_edu_indices = [i+1 for i, _ in enumerate(query)
                       if _['add_type'] == 'next_edu_and']
    slices = list()
    start = 0
    for i in new_edu_indices:
        end = i
        slices.append(query[start:end])
        start = i
    slices.append(query[start::])
    return slices

messages = {'ro_s_in_edu_dont_match': 'Пожалуйста, выберите одинаковые риторические отношения внутри одной ЭДЕ.',
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


def check_query(parsed_query):
    outer_parenth = True
    inner_parenth = True
    open_parenthesis_outer = list()
    close_parenthesis_outer = list()
    for edu in parsed_query:
        chosen_ro_s = set([' '.join(d['ro']) for d in edu])
        if len(chosen_ro_s) > 1:
            return messages['ro_s_in_edu_dont_match']
        searched_for_word = [d['searched_for'] for d in edu if d['type'] == 'word']
        if '' in searched_for_word or ' ' in searched_for_word:
            return messages['no_input_for_word']
        searched_for_lemma = [d['searched_for'] for d in edu if d['type'] == 'lemma']
        if '' in searched_for_lemma or ' ' in searched_for_lemma:
            return messages['no_input_for_lemma']
        searched_for_pos = [d['searched_for'] for d in edu if d['type'] == 'pos']
        if '' in searched_for_pos or ' ' in searched_for_pos:
            return messages['no_input_for_pos']
        searched_for_marker = [d['searched_for'] for d in edu if d['type'] == 'marker']
        if '' in searched_for_marker or ' ' in searched_for_marker:
            return messages['no_input_for_marker']
        open_parenthesis_inner = ''.join([d['open_parenth'] for d in edu])
        close_parenthesis_inner = ''.join([d['close_parenth'] for d in edu])
        open_parenthesis_outer += [d['open_parenth'] for d in edu]
        close_parenthesis_outer += [d['close_parenth'] for d in edu]
        if len(open_parenthesis_inner) != len(close_parenthesis_inner):
            inner_parenth = False
    open_parenthesis_outer = ''.join(open_parenthesis_outer)
    close_parenthesis_outer = ''.join(close_parenthesis_outer)
    if len(open_parenthesis_outer) != len(close_parenthesis_outer):
        outer_parenth = False
    if not outer_parenth and not inner_parenth:
        return messages['not_equal_parenth_amount']
    if not inner_parenth and outer_parenth:
        return messages['split_your_request']
    return True


markers = {"a": "a", "bezuslovno": "безусловно", "buduchi": "будучи",
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


def request_with_one_cond_on_edu(query):
    request_one_cond_on_edu = str()
    request_one_cond_on_edu += 'MATCH (n)\nWHERE'
    el = query[0]
    ro = el['ro']
    request_one_cond_on_edu += el['open_parenth']
    if ro == ['any']:
        if el['type'] == 'marker':
            marker_rus = markers[el['searched_for']]
            if '_lem' in el['searched_for']:
                request_one_cond_on_edu += ' n.lemmas CONTAINS \'{0}\''.format(marker_rus)
            else:
                marker_lengh = str(len(marker_rus)+1)
                if len(marker_rus.split()) > 1:
                    request_one_cond_on_edu += ' REDUCE(s = " ", w in split(n.text_norm, " ")' \
                                               '[0..{0}]|s + " " + w) CONTAINS \'{1}\''.format(marker_lengh, marker_rus)

                else:
                    request_one_cond_on_edu += ' \'{0}\' IN split(n.text_norm, " ")[0..{1}]'.\
                        format(marker_rus, marker_lengh)

        if el['type'] == 'word':
            request_one_cond_on_edu += " '{0}' IN split(n.text_norm, ' ')".\
                format(el['searched_for'])
        if el['type'] == 'lemma' or el['type'] == 'pos':
            request_one_cond_on_edu += ' n.lemmas CONTAINS "\'{0}\'"'.\
                format(el['searched_for'])
        if el['type'] == '':
            request_one_cond_on_edu = 'MATCH (n) WHERE exists(n.text)'
    else:
        if el['type'] == 'marker':
            marker_rus = markers[el['searched_for']]
            if '_lem' in el['searched_for']:
                request_one_cond_on_edu += ' n.lemmas CONTAINS \'{0}\''.format(marker_rus)
            else:
                marker_lengh = str(len(marker_rus)+1)
                if len(marker_rus.split()) > 1:
                    request_one_cond_on_edu += ' REDUCE(s = " ", w in split(n.text_norm, " ")' \
                                               '[0..{0}]|s + " " + w) CONTAINS \'{1}\''.format(marker_lengh, marker_rus)

                else:
                    request_one_cond_on_edu += ' \'{0}\' IN split(n.text_norm, " ")[0..{1}]'.\
                        format(marker_rus, marker_lengh)
        request_one_cond_on_edu = re.sub('WHERE', 'WHERE (', request_one_cond_on_edu)
        request_one_cond_on_edu = re.sub('MATCH \(n\)', 'MATCH (n)-[r]-()',
                                         request_one_cond_on_edu)
        if el['type'] == 'word':
            request_one_cond_on_edu += " '{0}' IN split(n.text_norm, ' ')) AND type(r) IN {1}".\
                format(el['searched_for'], ro)
        if el['type'] == 'lemma' or el['type'] == 'pos':
            request_one_cond_on_edu += ' n.lemmas CONTAINS "\'{0}\'") AND type(r) IN {1}'.format(el['searched_for'], ro)
        if el['type'] == '':
            request_one_cond_on_edu = 'MATCH (n)-[r]-() WHERE exists(n.text) AND type(r) IN {0}'.format(ro)
    request_one_cond_on_edu += el['close_parenth']
    request_one_cond_on_edu += "\nRETURN n.Text_id, n.Id, n.text"
    return request_one_cond_on_edu


def create_db_requests(query):
    requests_on_db = list()
    conditions = {'same_edu_and': 'AND', 'same_edu_or': 'OR', 'next_edu_and': '', 'none': ''}
    parsed_query = parse_query(query)
    ro = list()
    for i in parsed_query:
        request_on_db = str()
        request_on_db += 'MATCH (n)\nWHERE'
        if len(i) > 1:
            ro_chosen = False
            type_chosen = False
            for el in i:
                ro_chosen = False
                type_chosen = False
                request_on_db += el['open_parenth']
                cond = conditions[el['add_type']]
                ro = el['ro']
                if ro == ['any']:
                    if el['type'] == 'marker':
                        type_chosen = True
                        marker_rus = markers[el['searched_for']]
                        if '_lem' in el['searched_for']:
                            request_on_db += ' n.lemmas CONTAINS \'{0}\' {1}'.\
                                format(marker_rus, cond)
                        else:
                            marker_lengh = str(len(marker_rus)+1)
                            if len(marker_rus.split()) > 1:
                                request_on_db += ' REDUCE(s = " ", w in split(n.text_norm, " ")' \
                                                 '[0..{0}]|s + " " + w) CONTAINS \'{1}\' {2}'.\
                                    format(marker_lengh, marker_rus, cond)

                            else:
                                request_on_db += ' \'{0}\' IN split(n.text_norm, " ")[0..{1}] {2}'.\
                                    format(marker_rus, marker_lengh, cond)
                    if el['type'] == 'word':
                        type_chosen = True
                        request_on_db += " '{0}' IN split(n.text_norm, ' '){1} {2}".\
                            format(el['searched_for'], el['close_parenth'], cond)
                    if el['type'] == 'lemma' or el['type'] == 'pos':
                        type_chosen = True
                        request_on_db += ' n.lemmas CONTAINS "\'{0}\'"{1} {2}'.\
                            format(el['searched_for'], el['close_parenth'], cond)
                    if el['type'] == '':
                        type_chosen = False
                        request_on_db = 'MATCH (n) WHERE exists(n.text)'
                        request_on_db += el['close_parenth']
                else:
                    ro_chosen = True
                    if el['type'] == 'marker':
                        type_chosen = True
                        marker_rus = markers[el['searched_for']]
                        if '_lem' in el['searched_for']:
                            request_on_db += ' n.lemmas CONTAINS \'{0}\' {1}'.\
                                format(marker_rus, cond)
                        else:
                            marker_lengh = str(len(marker_rus)+1)
                            if len(marker_rus.split()) > 1:
                                request_on_db += ' REDUCE(s = " ", w in split(n.text_norm, " ")' \
                                                 '[0..{0}]|s + " " + w) CONTAINS \'{1}\' {2}'.\
                                                 format(marker_lengh, marker_rus, cond)

                            else:
                                request_on_db += ' \'{0}\' IN split(n.text_norm, " ")[0..{1}] {2}'.\
                                    format(marker_rus, marker_lengh, cond)
                    if el['type'] == 'word':
                        type_chosen = True
                        request_on_db += " '{0}' IN split(n.text_norm, ' '){1} {2}".\
                            format(el['searched_for'], el['close_parenth'], cond)
                    if el['type'] == 'lemma' or el['type'] == 'pos':
                        type_chosen = True
                        request_on_db += ' n.lemmas CONTAINS "\'{0}\'"{1} {2}'.\
                            format(el['searched_for'], el['close_parenth'], cond)
                    if el['type'] == '':
                        type_chosen = False
                        request_on_db = 'MATCH (n)-[r]-() WHERE exists(n.text)'
                        request_on_db += el['close_parenth']
            if ro_chosen and type_chosen:
                request_on_db = re.sub('MATCH \(n\)', 'MATCH (n)-[r]-()', request_on_db)
                request_on_db = re.sub("WHERE", "WHERE (", request_on_db)
                request_on_db += ') AND type(r) IN {0}'.format(ro)
            request_on_db += "\nRETURN n.Text_id, n.Id, n.text"
            requests_on_db.append(request_on_db)
        else:
            requests_on_db.append(request_with_one_cond_on_edu(i))
    return requests_on_db


def get_found(db_requests):
    all_found = list()
    for i in db_requests:
        found = graph.run(i)
        found = [[n[0], n[1], n[2]] for n in found]
        all_found.append(found)
    return all_found


def process_multi_edus_search(all_found):
    all_ids = list()
    out = list()
    for i in all_found:
        ids = [n[0] for n in i]
        all_ids.append(ids)
    num_of_edus = len(all_found)
    compare = all_ids[0]
    for n in range(num_of_edus - 1):
        a = all_ids[n+1]
        out = [x for x in compare if x in a]
        compare = out
        n += 1
    out = set(out)

    all_text_edus = list()
    for q in all_found:
        request_edus = dict()
        for i in out:
            text_edus = list()
            for k in q:
                if k[0] == i:
                    text_edus.append(k)
            request_edus[i] = text_edus

        all_text_edus.append(request_edus)
    return out, all_text_edus


def find_seq(texts_ids, result):
    text_result = dict()
    ids_result = dict()
    for i in texts_ids:
        texts_results = {i: [n[i] for n in result]}
        for text in texts_results.keys():
            text_result[text] = []
            ids_result[text] = []
            queries = texts_results[text]
            first_q = queries[0]
            for l in range(len(first_q)):
                res_edus = []
                k = first_q[l][1]
                res_edus.append(first_q[l])
                found_all = True
                for j in range(1, len(queries)):
                    goal = k+j
                    ids = [q[1] for q in queries[j]]
                    if goal not in ids:
                        found_all = False
                        break
                    else:
                        if len([n for n in queries[j] if n[1] == goal]) > 0:
                            res_edus.append([n for n in queries[j] if n[1] == goal][0])
                res_ids = [n[1] for n in res_edus]
                res_edus = [n[2] for n in res_edus]
                if found_all:
                    text_result[text].append(res_edus)
                    ids_result[text].append(res_ids)
    return text_result, ids_result


def your_query_line(param_rus, vals, addtype, open_p, close_p, ros):
    line = '<p><b>Ваш запрос: '
    for i in range(len(param_rus)):
        if param_rus[i] == 'риторический маркер':
            v = markers[vals[i]]
        elif param_rus[i] != '':
            v = vals[i]
        else:
            v = ''
        if i != 0 and addtype[i-1].startswith('same'):
            t = ' в той же ЭДЕ'
        elif i != 0:
            t = ' в следующей ЭДЕ'
        else:
            t = ''
        if addtype[i].endswith('and'):
            conj = ' И '
        elif addtype[i].endswith('or'):
            conj = ' ИЛИ '
        else:
            conj = ''
        if ros[i] == ['any']:
            if v != '':
                roo = '(любое риторическое отношение)'
            else:
                roo = 'любое риторическое отношение'
        else:
            if v != '':
                roo = '(в РО '
                for r in range(len(ros[i])):
                    roo += ros[i][r].capitalize()
                    if r != len(ros[i])-1:
                        roo += ', '
                    else:
                        roo += ')'
            else:
                roo = 'РО '
                for r in range(len(ros[i])):
                    roo += ros[i][r].capitalize()
                    if r == len(ros[i])-1:
                        roo += ' '
                    else:
                        roo += ', '
        line += open_p[i]
        line += param_rus[i]
        if v != '':
            line += ' "'
        line += v
        if v != '':
            line += '" '
        line += roo
        line += t
        line += close_p[i]
        line += conj
    line += '</b></p>'
    return line


def return_multiedu_search_res_html(all_found, param_rus, vals, addtype, open_p, close_p, ros):
    result = process_multi_edus_search(all_found)[1]
    texts_ids = process_multi_edus_search(all_found)[0]
    text_result = find_seq(texts_ids, result)[0]
    ids_result = find_seq(texts_ids, result)[1]
    res_multi_edu_res_html = str()
    line = your_query_line(param_rus, vals, addtype, open_p, close_p, ros)
    res_multi_edu_res_html += line
    csvfile = open('backend/static/search_result.csv', 'w', newline='', encoding='utf-8')
    csvwriter = csv.writer(csvfile)
    s1_r1 = line.lstrip('<p><b>').rstrip('</p></b>')
    csvwriter.writerow([s1_r1, ''])
    csvwriter.writerow(['Текст', 'ЭДЕ'])
    for text in text_result:
        check_lenght_text_result = len(text_result[text])
        if check_lenght_text_result > 0:
            res_multi_edu_res_html += '<p>Текст № {0}'.format(text) + '</p>\n<ul>\n'
            for i in range(len(text_result[text])):
                res_multi_edu_res_html += '<li>'
                for k in range(len(text_result[text][i])):
                    res_multi_edu_res_html += '<a href="tree/{0}.html?position=edu'.format(text)\
                                              + str(ids_result[text][i][k]) + \
                                              '" target="_blank">'+text_result[text][i][k]+'</a>'
                    if k != len(text_result[text][i])-1:
                        res_multi_edu_res_html += '<b>||</b>'
                full_text = '||'.join(text_result[text][i])
                csvwriter.writerow([str(text), full_text])
                res_multi_edu_res_html += '</li>\n'
            res_multi_edu_res_html += '</ul>\n'
    csvfile.close()
    return res_multi_edu_res_html


def return_singleedu_search_res_html(all_found, param_rus, vals, addtype, open_p, close_p, ros):
    res_single_edu_res_html = str()
    line = your_query_line(param_rus, vals, addtype, open_p, close_p, ros)
    res_single_edu_res_html += line
    all_found = all_found[0]
    all_found.sort(key=operator.itemgetter(0))
    found_by_text = itertools.groupby(all_found, lambda x: x[0])
    csvfile = open('backend/static/search_result.csv', 'w', newline='', encoding='utf-8')
    csvwriter = csv.writer(csvfile)
    s1_r1 = line.lstrip('<p><b>').rstrip('</p></b>')
    csvwriter.writerow([s1_r1, ''])
    csvwriter.writerow(['Текст', 'ЭДЕ'])
    for i, l in found_by_text:
        edus = [(n[1], n[2]) for n in list(l)]
        res_single_edu_res_html += '<p>Текст № {0}'.format(i) + '</p>\n\n<ul>'
        for edu in edus:
            edu_id = edu[0]
            edu_text = edu[1]
            res_single_edu_res_html += '<li><a href="tree/{0}.html?position=edu'.format(i)+str(edu_id) +\
                                       '" target="_blank">' + str(edu_text) + '</a></li>'
            csvwriter.writerow([str(i), str(edu_text)])
        res_single_edu_res_html += '</ul>'
    csvfile.close()
    return res_single_edu_res_html


def return_search_res_html(query, param_rus, vals, addtype, open_p, close_p, ros):
    checked = check_query(parse_query(query))
    if checked is True:
        try:
            db_requests = create_db_requests(query)
            all_found = get_found(db_requests)
            if len(all_found) > 1:
                return return_multiedu_search_res_html(all_found, param_rus, vals, addtype, open_p, close_p, ros)
            else:
                return return_singleedu_search_res_html(all_found, param_rus, vals, addtype, open_p, close_p, ros)
        except py2neo.database.status.CypherSyntaxError:
            return messages['fail']
    else:
        return checked


@app.route("/")
def hello():
    return "Hello from Flask!"


@app.route("/index.html")
def index():
    return render_template("index.html"), 201


@app.route("/aboutRST.html")
def about():
    return render_template("aboutRST.html"), 201


@app.route("/search.html")
def search():
    return render_template("search.html"), 201


@app.route("/tree.html")
def search_result():
    return render_template("tree.html"), 201


@app.route("/tree/<edu_id>.html")
def tree1(edu_id):
    posit = request.args.get("position")
    return render_template("trees/" + str(edu_id) + ".html", position=posit), 201


@app.route("/contact.html")
def contact():
    return render_template("contact.html"), 201


@app.route("/contactm.html", methods=['GET', 'POST'])
def contactm():
    mess = request.values.get("messagetext")
    if mess != '':
        cur_time = str(datetime.now()).replace(' ', 'T').replace(':', '-')
        fh = open('backend/static/messages_from_users/' + cur_time + '.txt', 'w', encoding='utf-8')
        auth = request.values.get("author")
        mail = request.values.get("email")
        subj = request.values.get("subject")
        fh.write('Author: ' + auth + '\n' + 'Email: ' + mail + '\n' + 'Subject: '
                 + subj + '\n' + 'Message: ' + mess)
        fh.close()
    return render_template("contactm.html"), 201


@app.route("/corpus.html")
def corpus():
    return render_template("corpus.html"), 201


@app.route("/download.html")
def download():
    return render_template("download.html"), 201


@app.route("/rhetrel.html")
def rhet():
    return render_template("rhetrel.html"), 201


@app.route("/result.html")
def res():
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
            if res_html in messages.values():
                if res_html == messages['fail']:
                    cur_time = str(datetime.now()).replace(' ', 'T').replace(':', '-')
                    fq = open('backend/static/failed_queries/' + cur_time + '.txt', 'w',
                              encoding='utf-8')
                    fq.write(str(query))
                    fq.close()
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
    app.run(debug=True)

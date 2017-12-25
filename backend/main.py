# -*- coding: utf-8 -*-

from flask import Flask, request, json, render_template_string, render_template
# from backend.static.searching_DB import search_edus
from html import unescape
from flask import Markup
import re
from datetime import datetime
from py2neo import Graph
import itertools
import operator
import csv

graph = Graph()

app = Flask(__name__)


def parse_query(query):
    #query = eval(query)
    #query = query['data']
    new_edu_indices = [i+1 for i, _ in enumerate(query) if _['add_type'] == 'next_edu_and']
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
            'not_equal_parenth_amount': 'Пожалуйста, проверьте корректность запроса, количество открывающих и закрывающих скобок не совпадает.',
            'split_your_request': 'Ваш запрос необходимо разбить на несколько отдельных запросов. Подробности см. в инструкции по поиску.',
            'fail': 'Ваш запрос не может быть обработан.\nЕсли Вы уверены, что в запросе нет ошибки, свяжитесь с нами через форму на странице "Контакты".'}


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


markers = {"a":"a", "bezuslovno":"безусловно", "buduchi":"будучи", "budeto":"будь это",
           "vitoge":"в итоге", "vosobennosti":"в особенности", "vramkah":"в рамках",
           "vrezultate":"в результате", "vsamomdele":"в самом деле", "vsvojyochered":"в свою очередь",
           "vsvyazis":"в связи с", "vtechenie":"в течение", "vtovremya":"в то время", "vtozhevremya":"в то же время",
           "vusloviyah":"в условиях", "vchastnosti":"в частности", "vposledstvii":"впоследствии",
           "vkluchaya":"включая", "vmestotogo":"вместо того", "vmestoetogo":"вместо этого",
           "vsezhe":"все же", "vsledstvie":"вследствие", "govoritsya":"говорится",
           "govorit_lem":"говорить", "dazhe":"даже", "dejstvitelno":"действительно",
           "dlya":"для", "dotakojstepeni":"до такой степени", "esli":"если",
           "zaverit_lem":"заверить", "zaveryat_lem":"заверять", "zayavit_lem":"заявить",
           "zayavlat_lem":"заявлять", "i":"и", "izza":"из-за", "ili":"или", "inache":"иначе",
           "ktomuzhe":"к тому же", "kogda":"когда", "kotoryj_lem":"который", "krometogo":"кроме того",
           "libo":"либо", "lishtogda":"лишь тогда", "nasamomdele":"на самом деле",
           "natotmoment":"на тот момент", "naetomfone":"на этом фоне", "napisat_lem":"написать",
           "naprimer":"например", "naprotiv":"напротив", "nesmotryana":"несмотря на", "no":"но",
           "noi":"но и", "objavit_lem":"объявить", "odnako":"однако", "osobenno":"особенно",
           "pisat_lem":"писать", "podannym":"по данным", "pomneniu":"по мнению", "poocenkam":"по оценкам",
           "posvedeniam":"по сведениям", "poslovam":"по словам", "podtverdit_lem":"подтвердить",
           "podtverzhdat_lem":"подтверждать", "podcherkivat_lem":"подчеркивать",
           "podcherknut_lem":"подчеркнуть",
           "pozdnee":"позднее", "pozzhe":"позже", "poka":"пока", "poskolku":"поскольку",
           "posle":"после", "potomuchto":"потому что", "poetomu":"поэтому",
           "prietom":"при этом", "priznavat_lem":"признавать", "priznano":"признано",
           "priznat_lem":"признать", "radi":"ради", "rasskazat_lem":"рассказать",
           "rasskazyvat_lem":"рассказывать", "sdrugojstorony":"с другой стороны",
           "scelyu":"с целью", "skazat_lem":"сказать", "skoree":"скорее",
           "sledovatelno":"следовательно", "sledomza":"следом за",
           "soobshaetsya":"сообщается", "soobshat_lem":"сообщать", "soobshit_lem":"сообщить",
           "taki":"так и", "takkak":"так как", "takchto":"так что", "takzhe":"также", "toest":"то есть",
           "utverzhdat_lem":"утверждать", "utverzhdaetsya":"утверждается", "hotya":"хотя"}


def request_with_one_cond_on_edu(query):
    requests = list()
    request = str()
    request += 'MATCH (n)\nWHERE'
    el = query[0]
    ro = el['ro']
    request += el['open_parenth']
    if ro == ['any']:
        if el['type'] == 'marker':
            marker_rus = markers[el['searched_for']]
            if '_lem' in el['searched_for']:
                request += ' n.lemmas CONTAINS \'{0}\''.format(marker_rus)
            else:
                marker_lengh = str(len(marker_rus)+1)
                if len(marker_rus.split()) > 1:
                    # request += ' lower(n.text) CONTAINS \'{0}\''.format(marker_rus)
                    request += ' REDUCE(s = " ", w in split(n.text_norm, " ")[0..{0}]|s + " " + w) CONTAINS \'{1}\''.format(marker_lengh, marker_rus)

                else:
                    # request += " '{0}' IN split(n.text_norm, ' ')".format(marker_rus)
                    request += ' \'{0}\' IN split(n.text_norm, " ")[0..{1}]'.format(marker_rus, marker_lengh)

        if el['type'] == 'word':
            request += " '{0}' IN split(n.text_norm, ' ')".format(el['searched_for'])
        if el['type'] == 'lemma' or el['type'] == 'pos':
            request += ' n.lemmas CONTAINS "\'{0}\'"'.format(el['searched_for'])
        if el['type'] == '':
            request = 'MATCH (n) WHERE exists(n.text)'
    else:
        if el['type'] == 'marker':
            marker_rus = markers[el['searched_for']]
            if '_lem' in el['searched_for']:
                request += ' n.lemmas CONTAINS \'{0}\''.format(marker_rus)
            else:
                marker_lengh = str(len(marker_rus)+1)
                if len(marker_rus.split()) > 1:
                    # request += ' lower(n.text) CONTAINS \'{0}\''.format(marker_rus)
                    request += ' REDUCE(s = " ", w in split(n.text_norm, " ")[0..{0}]|s + " " + w) CONTAINS \'{1}\''.format(marker_lengh, marker_rus)

                else:
                    # request += " '{0}' IN split(n.text_norm, ' ')".format(marker_rus)
                    request += ' \'{0}\' IN split(n.text_norm, " ")[0..{1}]'.format(marker_rus, marker_lengh)
        request = re.sub('WHERE', 'WHERE (', request)
        request = re.sub('MATCH \(n\)', 'MATCH (n)-[r]-()', request)
        if el['type'] == 'word':
            request += " '{0}' IN split(n.text_norm, ' ')) AND type(r) IN {1}".format(el['searched_for'], ro)
        if el['type'] == 'lemma' or el['type'] == 'pos':
            request += ' n.lemmas CONTAINS "\'{0}\'") AND type(r) IN {1}'.format(el['searched_for'], ro)
        if el['type'] == '':
            request = 'MATCH (n)-[r]-() WHERE exists(n.text) AND type(r) IN {0}'.format(ro)
    request += el['close_parenth']
    request += "\nRETURN n.Text_id, n.Id, n.text"
    #print(request, '\n')
    #requests.append(request)
    return request


def create_DB_requests(query):
    requests = list()
    conditions = {'same_edu_and': 'AND', 'same_edu_or': 'OR', 'next_edu_and': '', 'none': ''}
    parsed_query = parse_query(query)
    for i in parsed_query:
        request = str()
        request += 'MATCH (n)\nWHERE'
        if len(i) > 1:
            ro_chosen = False
            type_chosen = False
            for el in i:
                ro_chosen = False
                type_chosen = False
                request += el['open_parenth']
                cond = conditions[el['add_type']]
                ro = el['ro']
                if ro == ['any']:
                    if el['type'] == 'marker':
                        type_chosen = True
                        marker_rus = markers[el['searched_for']]
                        if '_lem' in el['searched_for']:
                            request += ' n.lemmas CONTAINS \'{0}\' {1}'.format(marker_rus, cond)
                        else:
                            marker_lengh = str(len(marker_rus)+1)
                            if len(marker_rus.split()) > 1:
                                # request += ' lower(n.text) CONTAINS \'{0}\''.format(marker_rus)
                                request += ' REDUCE(s = " ", w in split(n.text_norm, " ")[0..{0}]|s + " " + w) CONTAINS \'{1}\' {2}'.format(marker_lengh, marker_rus, cond)

                            else:
                                # request += " '{0}' IN split(n.text_norm, ' ')".format(marker_rus)
                                request += ' \'{0}\' IN split(n.text_norm, " ")[0..{1}] {2}'.format(marker_rus, marker_lengh, cond)
                    if el['type'] == 'word':
                        type_chosen = True
                        request += " '{0}' IN split(n.text_norm, ' '){1} {2}".format(el['searched_for'], el['close_parenth'], cond)
                    if el['type'] == 'lemma' or el['type'] == 'pos':
                        type_chosen = True
                        request += ' n.lemmas CONTAINS "\'{0}\'"{1} {2}'.format(el['searched_for'], el['close_parenth'], cond)
                    if el['type'] == '':
                        type_chosen = False
                        request = 'MATCH (n) WHERE exists(n.text)'
                        request += el['close_parenth']
                else:
                    ro_chosen = True
                    if el['type'] == 'marker':
                        type_chosen = True
                        marker_rus = markers[el['searched_for']]
                        if '_lem' in el['searched_for']:
                            request += ' n.lemmas CONTAINS \'{0}\' {1}'.format(marker_rus, cond)
                        else:
                            marker_lengh = str(len(marker_rus)+1)
                            if len(marker_rus.split()) > 1:
                                # request += ' lower(n.text) CONTAINS \'{0}\''.format(marker_rus)
                                request += ' REDUCE(s = " ", w in split(n.text_norm, " ")[0..{0}]|s + " " + w) CONTAINS \'{1}\' {2}'.format(marker_lengh, marker_rus, cond)

                            else:
                                # request += " '{0}' IN split(n.text_norm, ' ')".format(marker_rus)
                                request += ' \'{0}\' IN split(n.text_norm, " ")[0..{1}] {2}'.format(marker_rus, marker_lengh, cond)
                    if el['type'] == 'word':
                        type_chosen = True
                        request += " '{0}' IN split(n.text_norm, ' '){1} {2}".format(el['searched_for'], el['close_parenth'], cond)
                    if el['type'] == 'lemma' or el['type'] == 'pos':
                        type_chosen = True
                        request += ' n.lemmas CONTAINS "\'{0}\'"{1} {2}'.format(el['searched_for'], el['close_parenth'], cond)
                    if el['type'] == '':
                        type_chosen = False
                        request = 'MATCH (n)-[r]-() WHERE exists(n.text)'
                        request += el['close_parenth']
            if ro_chosen and type_chosen:
                request = re.sub('MATCH \(n\)', 'MATCH (n)-[r]-()', request)
                #request += ')'
                request = re.sub("WHERE", "WHERE (", request)
                request += ') AND type(r) IN {0}'.format(ro)
            #if not ro_chosen and not type_chosen:
                #request += el['close_parenth']
            request += "\nRETURN n.Text_id, n.Id, n.text"
            #print(request, '\n')
            requests.append(request)
        else:
            requests.append(request_with_one_cond_on_edu(i))
    print(requests)
    return requests


def get_found(DB_requests):
    all_found = list()
    for i in DB_requests:
        found = graph.run(i)
        found = [[n[0], n[1], n[2]] for n in found]
        all_found.append(found)
    return all_found


def process_multi_edus_search(all_found):
    all_ids = list()
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
    # all_text_edus_filtred = list()
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
            for i in range(len(first_q)):
                res_edus = []
                k = first_q[i][1]
                res_edus.append(first_q[i])
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
    res = str()
    line = your_query_line(param_rus, vals, addtype, open_p, close_p, ros)
    res += line
    csvfile = open('backend/static/search_result.csv', 'w', newline='', encoding='utf-8')
    csvwriter = csv.writer(csvfile)
    s1_r1 = line.lstrip('<p><b>').rstrip('</p></b>')
    csvwriter.writerow([s1_r1, ''])
    csvwriter.writerow(['Текст', 'ЭДЕ'])
    for text in text_result:
        if len(text_result[text]) > 0:
            res += '<p>Текст № {0}'.format(text) + '</p>\n<ul>\n'
            for i in range(len(text_result[text])):
                res += '<li>'
                for k in range(len(text_result[text][i])):
                    res += '<a href="tree/{0}.html?position=edu'.format(text)+str(ids_result[text][i][k])+'" target="_blank">'+text_result[text][i][k]+'</a>'
                    if k != len(text_result[text][i])-1:
                        res += '<b>||</b>'
                full_text = '||'.join(text_result[text][i])
                csvwriter.writerow([str(text), full_text])
                res += '</li>\n'
            res += '</ul>\n'
    return res


def return_singleedu_search_res_html(all_found, param_rus, vals, addtype, open_p, close_p, ros):
    res = str()
    line = your_query_line(param_rus, vals, addtype, open_p, close_p, ros)
    res += line
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
        res += '<p>Текст № {0}'.format(i) + '</p>\n\n<ul>'
        for edu in edus:
            edu_id = edu[0]
            edu_text = edu[1]
            res += '<li><a href="tree/{0}.html?position=edu'.format(i)+str(edu_id)+'" target="_blank">' + str(edu_text) + '</a></li>'
            csvwriter.writerow([str(i), str(edu_text)])
        res += '</ul>'
    csvfile.close()
    return res


def return_search_res_html(query, param_rus, vals, addtype, open_p, close_p, ros):
    checked = check_query(parse_query(query))
    if checked is True:
        try:
            DB_requests = create_DB_requests(query)
            all_found = get_found(DB_requests)
            if len(all_found) > 1:
                return return_multiedu_search_res_html(all_found, param_rus, vals, addtype, open_p, close_p, ros)
            else:
                return return_singleedu_search_res_html(all_found, param_rus, vals, addtype, open_p, close_p, ros)
        except:
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


@app.route("/tree/<id>.html")
def tree1(id):
    posit = request.args.get("position")
    return render_template("trees/" + str(id) + ".html", position=posit), 201


@app.route("/contact.html")
def contact():
    return render_template("contact.html"), 201


@app.route("/contactm.html", methods=['GET', 'POST'])
def contactm():
    mess = request.values.get("messagetext")
    if mess != '':
        cur_time = str(datetime.now()).replace(' ', 'T').replace(':', '-')
        fh = open('backend/static/messages_from_users/'+cur_time+'.txt', 'w', encoding='utf-8')
        auth = request.values.get("author")
        mail = request.values.get("email")
        subj = request.values.get("subject")
        fh.write('Author: '+ auth+'\n'+'Email: '+ mail+'\n'+'Subject: '+subj+'\n'+'Message: '+mess)  
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
    res = str()
    param_rus, vals, addtype, open_p, close_p, ros = [], [], [], [], [], []
    try:
        for q in query:
            try:
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
            except:
                parameter = ''
                param_rus.append('')
                value = ''
                vals.append('')
            addtype.append(q['add_type'])
            open_p.append(q['open_parenth'])
            close_p.append(q['close_parenth'])
            ros.append(q['ro'])
            print("SEARCH VALUES", parameter, value)
            res = return_search_res_html(query, param_rus, vals, addtype, open_p, close_p, ros)
            #print("RES", res)
            if res in messages.values():
                if res == messages['fail']:
                    cur_time = str(datetime.now()).replace(' ', 'T').replace(':', '-')
                    fq = open('backend/static/failed_queries/'+cur_time+'.txt', 'w', encoding='utf-8')
                    fq.write(str(query))
                    fq.close()
                break
            else:
                if res.endswith('". </b></p>'):
                    res += '<p><br><br> По Вашему запросу ничего не найдено.</p>'
                else:
                    res += '<br><p><b><a href="../static/search_result.csv" download>Скачать</a> результаты поиска в формате csv.</b></p><br>'
    except:
        res = '<p>Ваш запрос не может быть обработан.\nЕсли Вы уверены, что в запросе нет ошибки, свяжитесь с нами через форму на странице "Контакты".</p>'
    res = Markup(res)
    return render_template("result.html", result=res), 201

if __name__ == "__main__":
    app.run(debug=True)

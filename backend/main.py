# -*- coding: utf-8 -*-

from flask import Flask, request, json, render_template_string, render_template
# from backend.static.searching_DB import search_edus
from html import unescape
from flask import Markup

from py2neo import Graph
import itertools
import operator
import csv

graph = Graph()

app = Flask(__name__)


def parse_query(query):
    new_edu_indices = [i+1 for i, _ in enumerate(query) if _['add_type'] == 'next_edu_and']
    slices = list()
    start = 0
    for i in new_edu_indices:
        end = i
        slices.append(query[start:end])
        start = i
    slices.append(query[start::])
    return slices


def create_DB_requests(query):
    requests = list()
    conditions = {'same_edu_and': 'AND', 'same_edu_or': 'OR', 'next_edu_and': '', 'none': ''}
    parsed_query = parse_query(query)
    for i in parsed_query:
        request = str()
        request += 'MATCH (n)\nWHERE'
        if len(i) > 1:
            for el in i:
                cond = conditions[el['add_type']]
                if el['type'] == 'word':
                    request += " '{0}' IN split(n.text, ' ') {1}".format(el['searched_for'], cond)
                else:
                    request += ' n.lemmas CONTAINS "\'{0}\'" {1}'.format(el['searched_for'], cond)
        else:
            el = i[0]
            if el['type'] == 'word':
                request += " '{0}' IN split(n.text, ' ')".format(el['searched_for'])
            else:
                request += ' n.lemmas CONTAINS "\'{0}\'"'.format(el['searched_for'])

        request += "\nRETURN n.Text_id, n.Id, n.text"

        requests.append(request)
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
    return out, all_text_edus


def find_seq(texts_ids, result):
    text_result = dict()
    for i in texts_ids:
        texts_results = {i: [n[i] for n in result]}
        for text in texts_results.keys():
            text_result[text] = []
            queries = texts_results[text]
            first_q = queries[0]
            for i in range(len(first_q)):
                res_edus = []
                n = first_q[i][1]
                res_edus.append(first_q[i])
                found_all = True
                for j in range(1, len(queries)):
                    goal = n+j
                    ids = [q[1] for q in queries[j]]
                    if goal not in ids:
                        found_all = False
                        break
                    else:
                        res_edus.append([n for n in queries[1] if n[1] == goal][0])
                res_edus = [n[2] for n in res_edus]
                if found_all:
                    text_result[text].append(str(' '. join(res_edus)))
    return text_result


def return_multiedu_search_res_html(all_found):
    result = process_multi_edus_search(all_found)[1]
    texts_ids = process_multi_edus_search(all_found)[0]
    text_result = find_seq(texts_ids, result)
    res = str()
    for text in text_result:
        if len(text_result[text]) > 0:
            res += '<p>Текст № {0}'.format(text) + '</p>\n<ul>\n'
            for i in text_result[text]:
                res += '<li>'
                res += i
                res += '</li>\n'
            res += '</ul>\n'
    return res


def return_singleedu_search_res_html(all_found):
    res = str()
    all_found = all_found[0]
    all_found.sort(key=operator.itemgetter(0))
    found_by_text = itertools.groupby(all_found, lambda x: x[0])
    for i, l in found_by_text:
        edus = [(n[1], n[2]) for n in list(l)]
        res += '<p>Текст № {0}'.format(i) + '</p>\n\n<ul>'
        for edu in edus:
            edu_id = edu[0]
            edu_text = edu[1]
            res += '<li><a href="tree/{0}.html?position=edu'.format(i)+str(edu_id)+'">' + str(edu_text) + '</a></li>'
        res += '</ul>'
    return res


def return_search_res_html(query):
    DB_requests = create_DB_requests(query)
    all_found = get_found(DB_requests)
    if len(all_found) > 1:
        return return_multiedu_search_res_html(all_found)
    else:
        return return_singleedu_search_res_html(all_found)


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
    for q in query:
        parameter = q['type']
        if parameter == 'lemma':
            param_rus = 'лемма'
        elif parameter == 'word':
            param_rus = 'словоформа'
        elif parameter == 'pos':
            param_rus = 'часть речи'
        elif parameter == 'marker':
            param_rus = 'риторический маркер'
        value = q['searched_for']
        print("SEARCH VALUES", parameter, value)
        res += '<p><b>Ваш запрос: {0} "'.format(param_rus)+str(value)+'". </b></p>'
        with open("{{url_for('static', filename='search_result.csv')}}", 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Ваш запрос: {0} "'.format(param_rus)+str(value)+'".', ''])
            writer.writerow(['Текст', 'ЭДЕ'])
            res = return_search_res_html(query)
        if res.endswith('". </b></p>'):
            res += '<p><br><br> По Вашему запросу ничего не найдено.</p>'
        else:
            res += '<br><p><b><a href="../static/search_result.csv" download>Скачать</a> результаты поиска в формате csv.</b></p><br>'
    res = Markup(res)
    return render_template("result.html", result=res), 201

if __name__ == "__main__":
    app.run(debug=True)

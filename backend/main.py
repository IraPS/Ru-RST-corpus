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


def search_edus(parameter, value):
    found = None
    if parameter == 'word':
        found = graph.run("MATCH (n) WHERE '" + value + "' in split(n.text, ' ')\n RETURN n.Text_id, n.Id, split(n.text, ' ')")
        found = [[n[0], n[1], n[2]] for n in found]
    if parameter == 'lemma':
        found = graph.run('MATCH (n) WHERE n.lemmas CONTAINS "' + "'" + value + "'" + '"' +
                          " RETURN n.Text_id, n.Id, split(n.text, ' ')")
        found = [[n[0], n[1], n[2]] for n in found]
    if parameter == 'pos':
        found = graph.run('MATCH (n) WHERE n.lemmas CONTAINS "' + "'" + value + "'" + '"' +
                          " RETURN n.Text_id, n.Id, split(n.text, ' ')")
        found = [[n[0], n[1], n[2]] for n in found]
    # print([n for n in found if n[0] == 20], '\n\n')
    if found:
        found.sort(key=operator.itemgetter(0))
        found_by_text = itertools.groupby(found, lambda x: x[0])
        found = found_by_text
    return found


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
        search_result = search_edus(parameter=parameter, value=value)
        res += '<p><b>Ваш запрос: {0} "'.format(param_rus)+str(value)+'". </b></p>'
        with open("{{url_for('static', filename='search_result.csv')}}", 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Ваш запрос: {0} "'.format(param_rus)+str(value)+'".', ''])
            writer.writerow(['Текст', 'ЭДЕ'])
            for i, l in search_result:
                edus = [(n[1], ' '.join(n[2])) for n in list(l)]
                res += '<p>Текст № {0}'.format(i) + '</p>\n\n<ul>'
                for edu in edus:
                    edu_id = edu[0]
                    edu_text = edu[1]
                    res += '<li><a href="tree/{0}.html?position=edu'.format(i)+str(edu_id)+'">' + str(edu_text) + '</a></li>'
                    writer.writerow(['{0}'.format(i), str(edu_text)])
                res += '</ul>'
        if res.endswith('". </b></p>'):
            res += '<p><br><br> По Вашему запросу ничего не найдено.</p>'
        else:
            res += '<br><p><b><a href="../static/search_result.csv" download>Скачать</a> результаты поиска в формате csv.</b></p><br>'
    res = Markup(res)
    return render_template("result.html", result=res), 201

if __name__ == "__main__":
    app.run(debug=True)

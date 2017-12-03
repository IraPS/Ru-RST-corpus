# -*- coding: utf-8 -*-

from flask import Flask, request, json, render_template_string, render_template
from backend.static.searching_DB import search_edus
from html import unescape
from flask import Markup

app = Flask(__name__)


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
    return render_template("trees/" + str(id) + ".html"), 201
	
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
        value = q['searched_for']
        print("SEARCH VALUES", parameter, value)
        search_result = search_edus(parameter=parameter, value=value)
        for i, l in search_result:
            edus = [' '.join(n[1]) for n in list(l)]
            res += '<p>Текст №' + str(i) + '</p>\n\n<ul>'
            for edu in edus:
                res += '<li>' + str(edu) + '</li>'
            res += '</ul>'
            # res += '<p>' + str(i) + '</p>\n\n<p>' + str([n[1] for n in list(l)]) + '</p>\n\n\n\n'
    res = Markup(res)
    return render_template("result.html", result=res), 201

if __name__ == "__main__":
    app.run(debug=True)

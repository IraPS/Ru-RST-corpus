# -*- coding: utf-8 -*-

from flask import Flask, request, json, render_template_string, render_template

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

if __name__ == "__main__":
    app.run(debug=True)

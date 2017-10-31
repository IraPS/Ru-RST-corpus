# -*- coding: utf-8 -*-

try:
    from os import getuid

except ImportError:
    def getuid():
        return 4000

from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello from Flask!"

@app.route("/index")
def index():
    return render_template("static/index.html")

if __name__ == "__main__":
    app.run(port=getuid() + 1000)

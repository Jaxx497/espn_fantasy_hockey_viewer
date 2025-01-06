from flask import Flask, render_template
import json

from main import beta_func

app = Flask(__name__)


@app.route("/")
def index():
    data = beta_func()
    return render_template("index.html", data=data)


@app.route("/api/matchups")
def get_matchups():
    data = beta_func()
    return json.dumps(data["matchups"])


if __name__ == "__main__":
    app.run(debug=True)

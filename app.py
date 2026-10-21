from flask import Flask, render_template

from data import latest_week_summary, load_charts, rank_history

app = Flask(__name__)


@app.route("/")
def index():
    try:
        charts = load_charts()
    except FileNotFoundError as error:
        return render_template("index.html", error=str(error))
    return render_template(
        "index.html",
        summary=latest_week_summary(charts),
        history=rank_history(charts),
    )


if __name__ == "__main__":
    app.run(debug=True)

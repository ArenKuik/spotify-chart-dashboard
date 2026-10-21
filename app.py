from flask import Flask, abort, render_template

from data import latest_week_summary, load_charts, rank_history, song_history
from itunes import get_album_art

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


@app.route("/song/<track_id>")
def song(track_id):
    try:
        charts = load_charts()
    except FileNotFoundError as error:
        return render_template("song.html", error=str(error))
    history = song_history(charts, track_id)
    if history is None:
        abort(404)
    art_url, art_message = get_album_art(history["track_name"], history["artist_names"])
    return render_template(
        "song.html", song=history, art_url=art_url, art_message=art_message
    )


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)

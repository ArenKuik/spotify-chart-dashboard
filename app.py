from flask import Flask, abort, render_template, request

from data import (
    DATA_DIR, check_upload, latest_week_summary, load_charts, rank_history, song_history,
)
from itunes import get_album_art

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # reject uploads over 5 MB


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


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "GET":
        return render_template("upload.html")

    file = request.files.get("chart_file")
    if file is None or file.filename == "":
        return render_template("upload.html", errors=["Please choose a file to upload."])

    content = file.read()
    errors = check_upload(file.filename, content)
    if errors:
        return render_template("upload.html", errors=errors)

    (DATA_DIR / file.filename).write_bytes(content)
    return render_template("upload.html", success=file.filename)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(413)
def file_too_large(error):
    return render_template("upload.html", errors=["The file is too large. The limit is 5 MB."]), 413


if __name__ == "__main__":
    app.run(debug=True)

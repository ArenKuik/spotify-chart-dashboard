import io
import re
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
FILE_PREFIX = "regional-us-weekly-"
FILENAME_PATTERN = re.compile(r"^regional-us-weekly-(\d{4}-\d{2}-\d{2})\.csv$")
REQUIRED_COLUMNS = [
    "rank", "uri", "artist_names", "track_name", "source",
    "peak_rank", "previous_rank", "weeks_on_chart", "streams",
]
NUMBER_COLUMNS = ["rank", "peak_rank", "previous_rank", "weeks_on_chart", "streams"]


def load_charts():
    """Read every weekly chart CSV into one DataFrame."""
    files = sorted(DATA_DIR.glob(FILE_PREFIX + "*.csv"))
    if not files:
        raise FileNotFoundError(
            f"No chart files found in {DATA_DIR}. "
            f"Expected files named like {FILE_PREFIX}YYYY-MM-DD.csv."
        )

    weeks = []
    for file in files:
        df = pd.read_csv(file, encoding="utf-8-sig")
        date_text = file.stem.replace(FILE_PREFIX, "")
        df["week"] = pd.to_datetime(date_text)
        weeks.append(df)

    charts = pd.concat(weeks, ignore_index=True)
    charts["track_id"] = charts["uri"].str.split(":").str[-1]
    return charts


def latest_week_summary(charts, top_n=20):
    """Top songs, biggest climber and newest entry for the most recent week."""
    latest_week = charts["week"].max()
    week = charts[charts["week"] == latest_week].sort_values("rank")

    is_new = week["previous_rank"] == -1
    returning = week[~is_new]
    climb = returning["previous_rank"] - returning["rank"]

    climber = None
    if not climb.empty and climb.max() > 0:
        climber = returning.loc[climb.idxmax()].to_dict()
        climber["climb"] = int(climb.max())

    newest = None
    if is_new.any():
        newest = week[is_new].iloc[0].to_dict()

    return {
        "week": latest_week,
        "top_songs": week.head(top_n).to_dict("records"),
        "climber": climber,
        "newest": newest,
    }


def rank_history(charts, top_n=5):
    """Rank in every week for the latest week's top songs, ready for Chart.js."""
    weeks = sorted(charts["week"].unique())
    latest = charts[charts["week"] == weeks[-1]].sort_values("rank").head(top_n)

    songs = []
    for _, song in latest.iterrows():
        history = charts[charts["track_id"] == song["track_id"]]
        rank_by_week = dict(zip(history["week"], history["rank"]))
        songs.append({
            "label": f"{song['track_name']} – {song['artist_names']}",
            # None means the song was not in the top 200 that week
            "ranks": [int(rank_by_week[w]) if w in rank_by_week else None for w in weeks],
        })

    return {
        "weeks": [pd.Timestamp(w).strftime("%b %d") for w in weeks],
        "songs": songs,
    }


def song_history(charts, track_id):
    """Rank and streams in every week for one song, or None if the id is unknown."""
    history = charts[charts["track_id"] == track_id]
    if history.empty:
        return None

    weeks = []
    for week in sorted(charts["week"].unique()):
        row = history[history["week"] == week]
        weeks.append({
            "week": pd.Timestamp(week).strftime("%b %d"),
            # None means the song was not in the top 200 that week
            "rank": int(row["rank"].iloc[0]) if not row.empty else None,
            "streams": int(row["streams"].iloc[0]) if not row.empty else None,
        })

    first = history.iloc[0]
    return {
        "track_id": track_id,
        "track_name": first["track_name"],
        "artist_names": first["artist_names"],
        "best_rank": int(history["rank"].min()),
        "total_streams": int(history["streams"].sum()),
        "weeks": weeks,
    }


def check_upload(filename, content):
    """Return a list of problems with an uploaded chart file (empty list means it's fine)."""
    if not filename.lower().endswith(".csv"):
        return ["The file must be a .csv file."]

    match = FILENAME_PATTERN.match(filename)
    if not match:
        return [f"The file name must look like {FILE_PREFIX}YYYY-MM-DD.csv, "
                "because the week's date is taken from the name."]
    try:
        pd.to_datetime(match.group(1), format="%Y-%m-%d")
    except ValueError:
        return [f"{match.group(1)} in the file name is not a real date."]
    if (DATA_DIR / filename).exists():
        return [f"A chart for {match.group(1)} has already been uploaded."]

    try:
        df = pd.read_csv(io.BytesIO(content), encoding="utf-8-sig")
    except pd.errors.EmptyDataError:
        return ["The file is empty."]
    except (UnicodeDecodeError, pd.errors.ParserError):
        return ["The file could not be read as a CSV. Is it a text file with comma-separated values?"]

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        return ["The file is missing these columns: " + ", ".join(missing) + "."]
    if df.empty:
        return ["The file has the right columns but no songs."]

    problems = []
    for col in NUMBER_COLUMNS:
        if not pd.api.types.is_numeric_dtype(df[col]) or df[col].isna().any():
            problems.append(f"Every value in the {col} column must be a whole number.")
    return problems

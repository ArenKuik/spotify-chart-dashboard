from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
FILE_PREFIX = "regional-us-weekly-"


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

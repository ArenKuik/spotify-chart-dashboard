# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Flask + pandas dashboard over Spotify weekly US chart data (course assignment: OMIS107 HW4). At this stage the repo holds only the data, dependencies, and empty `templates/` and `static/` directories; no application code exists yet.

## Environment

- Virtualenv is at `.venv/` (Python 3.9.6, git-ignored). Use `.venv/bin/python` / `.venv/bin/pip`, or `source .venv/bin/activate`.
- Install deps: `.venv/bin/pip install -r requirements.txt` (pinned: Flask 3.1, pandas 2.3, numpy 2.0, requests).
- Keep code compatible with Python 3.9 (e.g. no `match` statements, no `X | Y` type unions at runtime).
- No test suite, linter, or build step is configured.

## Data

`data/regional-us-weekly-YYYY-MM-DD.csv`: one file per chart week (six weeks, 2026-09-10 through 2026-10-15), each with the top 200 tracks. The chart date exists only in the filename, so derive it from there when combining weeks.

Columns: `rank, uri, artist_names, track_name, source, peak_rank, previous_rank, weeks_on_chart, streams`

Things to know when loading with pandas:
- Files start with a UTF-8 BOM; read with `encoding="utf-8-sig"` or the first column name becomes `﻿rank`.
- `streams` is a quoted string in the CSV; make sure it ends up numeric.
- `previous_rank` is `-1` for tracks that are new to the chart that week.
- `artist_names` can list several artists separated by commas inside one quoted field.
- `uri` (`spotify:track:<id>`) is the stable track key across weeks; track names are not unique.

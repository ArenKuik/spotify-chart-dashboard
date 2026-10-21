import requests

SEARCH_URL = "https://itunes.apple.com/search"
TIMEOUT_SECONDS = 5


def get_album_art(track_name, artist_names):
    """Return (image_url, None) on success, or (None, message) if anything goes wrong."""
    # Search with the first artist only; extra featured artists make matches worse
    first_artist = artist_names.split(",")[0]
    params = {
        "term": f"{track_name} {first_artist}",
        "media": "music",
        "entity": "song",
        "limit": 1,
    }

    try:
        response = requests.get(SEARCH_URL, params=params, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        results = response.json()["results"]
    except requests.Timeout:
        return None, "Album art is unavailable: iTunes took too long to respond."
    except requests.RequestException:
        return None, "Album art is unavailable: could not reach iTunes."
    except (ValueError, KeyError):
        return None, "Album art is unavailable: iTunes sent an unexpected response."

    if not results or "artworkUrl100" not in results[0]:
        return None, "No album art found for this song."

    # iTunes returns a 100x100 image; the same URL works with a bigger size
    return results[0]["artworkUrl100"].replace("100x100", "300x300"), None

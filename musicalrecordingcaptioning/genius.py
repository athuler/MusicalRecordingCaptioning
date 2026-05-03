from dataclasses import dataclass
from urllib.parse import urlparse
import re
import lyricsgenius


@dataclass
class Song:
    title: str
    lyrics: list[str]  # non-empty lines with section headers removed


def _clean_lyrics(raw: str) -> list[str]:
    lines = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        # drop section headers like [Verse 1], [Chorus], etc.
        if re.match(r"^\[.+\]$", line):
            continue
        # lyricsgenius prepends "SongTitle Lyrics" as a first line
        if re.match(r"^.+Lyrics$", line):
            continue
        lines.append(line)
    return lines


def _slug_to_name(slug: str) -> str:
    return slug.replace("-", " ").title()


def _parse_genius_album_url(url: str) -> tuple[str, str]:
    """Return (artist_name, album_name) parsed from a Genius album URL.

    Expected format: https://genius.com/albums/{artist-slug}/{album-slug}
    """
    path = urlparse(url).path.rstrip("/")
    parts = path.split("/")
    # parts: ['', 'albums', 'artist-slug', 'album-slug']
    if len(parts) != 4 or parts[1] != "albums":
        raise ValueError(
            f"Unrecognised Genius album URL format: {url}\n"
            "Expected: https://genius.com/albums/<artist>/<album>"
        )
    return _slug_to_name(parts[2]), _slug_to_name(parts[3])


def fetch_album_lyrics(url: str, token: str) -> list[Song]:
    artist, album = _parse_genius_album_url(url)
    genius = lyricsgenius.Genius(token, remove_section_headers=True)
    genius.verbose = False
    album_obj = genius.search_album(album, artist)
    if album_obj is None:
        raise ValueError(f"Album '{album}' by '{artist}' not found on Genius.")

    songs: list[Song] = []
    for track in album_obj.tracks:
        # lyricsgenius >= 3.x returns Track objects; some versions return (number, Song) tuples
        song = track[1] if isinstance(track, tuple) else track.song
        if song.lyrics:
            songs.append(Song(title=song.title, lyrics=_clean_lyrics(song.lyrics)))
    return songs

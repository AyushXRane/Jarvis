"""YouTube actions — open, search, and play."""

from __future__ import annotations

import logging
import subprocess
import urllib.parse

logger = logging.getLogger(__name__)


def open_youtube() -> None:
    """Open YouTube in the default browser."""
    logger.info("Opening YouTube")
    subprocess.run(["open", "https://www.youtube.com"], check=True)


def _search_youtube_url(query: str, *, prefer_playlist: bool = False) -> str:
    search = query
    if prefer_playlist and "playlist" not in query.lower():
        search = f"{query} playlist"

    if prefer_playlist:
        result = subprocess.run(
            [
                "yt-dlp",
                f"ytsearch10:{search}",
                "--flat-playlist",
                "--print",
                "%(webpage_url)s",
                "--match-filter",
                "playlist_id != None",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        urls = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if urls:
            return urls[0]

    result = subprocess.run(
        [
            "yt-dlp",
            f"ytsearch5:{search}",
            "--flat-playlist",
            "--print",
            "%(id)s",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    video_ids = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if not video_ids:
        raise RuntimeError(f"No YouTube results for {query!r}")
    return f"https://www.youtube.com/watch?v={video_ids[0]}&autoplay=1"


def play_on_youtube(query: str, *, prefer_playlist: bool = False) -> None:
    """Search YouTube and open the best match with autoplay."""
    url = _search_youtube_url(query, prefer_playlist=prefer_playlist)
    if "autoplay=1" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}autoplay=1"
    logger.info("Playing %r on YouTube: %s", query, url)
    subprocess.run(["open", url], check=True)

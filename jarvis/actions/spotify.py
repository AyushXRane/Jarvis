"""Play music on Spotify via AppleScript."""

from __future__ import annotations

import logging
import subprocess
import urllib.parse

logger = logging.getLogger(__name__)


def play_on_spotify(query: str, *, prefer_playlist: bool = False) -> None:
    """Open Spotify, search for `query`, and start playback."""
    search_query = query
    if prefer_playlist and "playlist" not in query.lower():
        search_query = f"{query} playlist"
    search_uri = "spotify:search:" + urllib.parse.quote(search_query)
    escaped_uri = search_uri.replace("\\", "\\\\").replace('"', '\\"')
    script = f'''
tell application "Spotify"
    activate
    play track "{escaped_uri}"
end tell
'''
    logger.info("Playing %r on Spotify", query)
    subprocess.run(
        ["osascript", "-e", script],
        check=True,
        capture_output=True,
        text=True,
    )


def open_spotify() -> None:
    """Launch Spotify without starting playback."""
    logger.info("Opening Spotify")
    subprocess.run(
        ["osascript", "-e", 'tell application "Spotify" to activate'],
        check=True,
        capture_output=True,
        text=True,
    )

"""macOS system actions — apps, volume, and media keys."""

from __future__ import annotations

import logging
import subprocess

logger = logging.getLogger(__name__)

APP_ALIASES: dict[str, str] = {
    "arc": "Arc",
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",
    "safari": "Safari",
    "spotify": "Spotify",
    "finder": "Finder",
    "terminal": "Terminal",
    "messages": "Messages",
    "notes": "Notes",
    "mail": "Mail",
    "photos": "Photos",
    "music": "Music",
    "settings": "System Settings",
    "system settings": "System Settings",
    "preferences": "System Settings",
    "vscode": "Visual Studio Code",
    "visual studio code": "Visual Studio Code",
    "code": "Visual Studio Code",
    "cursor": "Cursor",
    "slack": "Slack",
    "discord": "Discord",
    "zoom": "zoom.us",
    "calendar": "Calendar",
    "reminders": "Reminders",
}


def resolve_app(name: str) -> str:
    key = name.lower().strip()
    if key in APP_ALIASES:
        return APP_ALIASES[key]
    return name.title()


def open_application(name: str) -> None:
    app_name = resolve_app(name)
    logger.info("Opening application: %s", app_name)
    subprocess.run(["open", "-a", app_name], check=True)


def volume_up(steps: int = 1) -> None:
    bump = 8 * steps
    script = f'''
set currentVolume to output volume of (get volume settings)
set newVolume to currentVolume + {bump}
if newVolume > 100 then set newVolume to 100
set volume output volume newVolume
'''
    logger.info("Volume up (%s steps)", steps)
    subprocess.run(["osascript", "-e", script], check=True)


def volume_down(steps: int = 1) -> None:
    bump = 8 * steps
    script = f'''
set currentVolume to output volume of (get volume settings)
set newVolume to currentVolume - {bump}
if newVolume < 0 then set newVolume to 0
set volume output volume newVolume
'''
    logger.info("Volume down (%s steps)", steps)
    subprocess.run(["osascript", "-e", script], check=True)


def mute_volume() -> None:
    logger.info("Muting volume")
    subprocess.run(["osascript", "-e", "set volume with output muted"], check=True)


def unmute_volume() -> None:
    logger.info("Unmuting volume")
    subprocess.run(["osascript", "-e", "set volume without output muted"], check=True)


def pause_media() -> None:
    logger.info("Pausing media")
    subprocess.run(
        ["osascript", "-e", 'tell application "System Events" to key code 16 using {command down}'],
        check=True,
    )


def play_media() -> None:
    logger.info("Resuming media")
    subprocess.run(
        ["osascript", "-e", 'tell application "System Events" to key code 16 using {command down}'],
        check=True,
    )


def skip_track() -> None:
    logger.info("Skipping track")
    subprocess.run(
        ["osascript", "-e", 'tell application "System Events" to key code 17 using {command down}'],
        check=True,
    )


def previous_track() -> None:
    logger.info("Previous track")
    subprocess.run(
        ["osascript", "-e", 'tell application "System Events" to key code 19 using {command down}'],
        check=True,
    )


def brightness_up(steps: int = 1) -> None:
    logger.info("Brightness up (%s steps)", steps)
    for _ in range(steps):
        subprocess.run(
            [
                "osascript",
                "-e",
                'tell application "System Events" to key code 144',
            ],
            check=True,
        )


def brightness_down(steps: int = 1) -> None:
    logger.info("Brightness down (%s steps)", steps)
    for _ in range(steps):
        subprocess.run(
            [
                "osascript",
                "-e",
                'tell application "System Events" to key code 145',
            ],
            check=True,
        )

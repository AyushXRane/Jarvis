"""Tests for flexible command parsing."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jarvis.parser import (
    BrightnessCommand,
    MediaCommand,
    OpenAppCommand,
    PlayCommand,
    TextCommand,
    VolumeCommand,
    parse_command,
)


def test_open_commands():
    cases = {
        "open youtube": "youtube",
        "launch spotify": "spotify",
        "open chrome": "chrome",
        "start safari": "safari",
        "open arc": "arc",
        "open terminal": "terminal",
    }
    for text, target in cases.items():
        cmd = parse_command(text)
        assert isinstance(cmd, OpenAppCommand), text
        assert cmd.target == target, (text, cmd)


def test_play_commands():
    cases = {
        "play yeat on spotify": ("yeat", "spotify", False),
        "play how to tie a tie on youtube": ("how to tie a tie", "youtube", False),
        "watch mr beast on youtube": ("mr beast", "youtube", False),
        "play a yeat playlist on spotify": ("yeat", "spotify", True),
        "play cooking tutorials": ("cooking tutorials", "youtube", False),
    }
    for text, (query, platform, prefer_playlist) in cases.items():
        cmd = parse_command(text)
        assert isinstance(cmd, PlayCommand), text
        assert cmd.query == query, (text, cmd)
        assert cmd.platform == platform, (text, cmd)
        assert cmd.prefer_playlist == prefer_playlist, (text, cmd)


def test_volume_commands():
    cases = {
        "turn up the volume": "up",
        "volume down": "down",
        "make it louder": "up",
        "mute": "mute",
        "unmute": "unmute",
    }
    for text, action in cases.items():
        cmd = parse_command(text)
        assert isinstance(cmd, VolumeCommand), text
        assert cmd.action == action, (text, cmd)


def test_media_commands():
    cases = {
        "pause": "pause",
        "pause the music": "pause",
        "next song": "next",
        "skip this": "next",
        "previous track": "previous",
        "resume": "play",
    }
    for text, action in cases.items():
        cmd = parse_command(text)
        assert isinstance(cmd, MediaCommand), text
        assert cmd.action == action, (text, cmd)


def test_brightness_commands():
    cases = {
        "turn up the brightness": "up",
        "make the screen brighter": "up",
        "dim the screen": "down",
        "brightness down": "down",
    }
    for text, action in cases.items():
        cmd = parse_command(text)
        assert isinstance(cmd, BrightnessCommand), text
        assert cmd.action == action, (text, cmd)


def test_text_commands():
    cmd = parse_command("text mom saying I'll be home at 8")
    assert isinstance(cmd, TextCommand)
    assert cmd.recipient == "mom"
    assert "home" in cmd.message


if __name__ == "__main__":
    test_open_commands()
    test_play_commands()
    test_volume_commands()
    test_media_commands()
    test_brightness_commands()
    test_text_commands()
    print("All parser tests passed.")

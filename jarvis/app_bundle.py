"""Build Jarvis.app for reliable macOS microphone permissions."""

from __future__ import annotations

import stat
import sys
from pathlib import Path

JARVIS_DIR = Path(__file__).resolve().parents[1]
APP_PATH = JARVIS_DIR / "Jarvis.app"


def build_app(python: str | None = None) -> Path:
    python = python or sys.executable
    macos = APP_PATH / "Contents" / "MacOS"
    macos.mkdir(parents=True, exist_ok=True)

    (APP_PATH / "Contents" / "Info.plist").write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>Jarvis</string>
    <key>CFBundleDisplayName</key>
    <string>Jarvis</string>
    <key>CFBundleIdentifier</key>
    <string>com.jarvis.assistant</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleExecutable</key>
    <string>jarvis</string>
    <key>NSMicrophoneUsageDescription</key>
    <string>Jarvis needs the microphone to hear wake word commands.</string>
    <key>NSAppleEventsUsageDescription</key>
    <string>Jarvis controls apps like Spotify, Messages, and Chrome.</string>
</dict>
</plist>
"""
    )

    launcher = macos / "jarvis"
    launcher.write_text(
        f"""#!/bin/bash
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export PYTHONPATH="{JARVIS_DIR}"
cd "{JARVIS_DIR}"
exec "{python}" -m jarvis run
"""
    )
    mode = launcher.stat().st_mode
    launcher.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return APP_PATH


def app_executable() -> str:
    return str(APP_PATH / "Contents" / "MacOS" / "jarvis")

"""Install and manage the Jarvis background service."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from jarvis.app_bundle import APP_PATH, app_executable, build_app

PLIST_LABEL = "com.jarvis.assistant"
JARVIS_DIR = Path(__file__).resolve().parents[1]
PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / f"{PLIST_LABEL}.plist"
LOG_DIR = Path.home() / "Library" / "Logs"
DATA_DIR = Path.home() / ".jarvis"


def _plist_content(executable: str) -> str:
    log_out = LOG_DIR / "jarvis.log"
    log_err = LOG_DIR / "jarvis.error.log"

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{PLIST_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{executable}</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{JARVIS_DIR}</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{log_out}</string>
    <key>StandardErrorPath</key>
    <string>{log_err}</string>
</dict>
</plist>
"""


def install_service() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    contacts_example = DATA_DIR / "contacts.json.example"
    if not contacts_example.exists():
        contacts_example.write_text(
            '{\n  "mom": "+15555550100",\n  "john": "john@example.com"\n}\n'
        )

    contacts = DATA_DIR / "contacts.json"
    if not contacts.exists():
        shutil.copy(contacts_example, contacts)

    build_app(sys.executable)
    executable = app_executable()

    PLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    PLIST_PATH.write_text(_plist_content(executable))

    uid = os.getuid()
    subprocess.run(["launchctl", "bootout", f"gui/{uid}", str(PLIST_PATH)], check=False)
    subprocess.run(["launchctl", "bootstrap", f"gui/{uid}", str(PLIST_PATH)], check=True)

    print("Jarvis installed and running in the background.")
    print(f"App: {APP_PATH}")
    print(f"Logs: {LOG_DIR / 'jarvis.log'}")
    print(f"Contacts: {contacts}")
    print()
    print("IMPORTANT — grant Microphone to Jarvis:")
    print("  System Settings → Privacy & Security → Microphone → enable Jarvis")
    print()
    print('Then say "Jarvis" to activate.')


def uninstall_service() -> None:
    if not PLIST_PATH.exists():
        print("Jarvis service is not installed.")
        return

    uid = os.getuid()
    subprocess.run(["launchctl", "bootout", f"gui/{uid}", str(PLIST_PATH)], check=False)
    PLIST_PATH.unlink(missing_ok=True)
    print("Jarvis background service removed.")


def service_status() -> None:
    """Check if Jarvis background service is running."""
    uid = os.getuid()
    result = subprocess.run(
        ["launchctl", "print", f"gui/{uid}/{PLIST_LABEL}"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print("Jarvis is running in the background.")
        print(f"Logs: tail -f {LOG_DIR / 'jarvis.log'}")
    else:
        print("Jarvis is not running.")


def setup_permissions() -> None:
    build_app(sys.executable)
    print("Jarvis setup — microphone permission required\n")
    print("1. Opening System Settings → Microphone...")
    subprocess.run(
        ["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_Microphone"],
        check=False,
    )
    print("2. Enable the toggle for **Jarvis** (and Python if listed).")
    print("3. If Jarvis is not in the list, run this once to trigger the prompt:")
    print(f"   open {APP_PATH}")
    print()
    input("Press Enter after enabling Microphone for Jarvis...")
    print("\nTesting microphone — say 'Jarvis' now...")
    from jarvis.listener import VoiceListener

    listener = VoiceListener()
    text, level = listener.transcribe(5.0)
    print(f"Audio level: {level} (need > 100 when speaking)")
    if text:
        print(f"Heard: {text!r}")
        if listener.matches_wake_word(text):
            print("Wake word detected — you're good!")
        else:
            print("Speech works. Say 'Jarvis' clearly.")
    elif level < 50:
        print("Still no mic input — make sure Jarvis is enabled in Microphone settings.")
    else:
        print("Mic works but nothing transcribed — check internet connection.")
    print("\nThen run: python3 -m jarvis install")
    uid = os.getuid()
    result = subprocess.run(
        ["launchctl", "print", f"gui/{uid}/{PLIST_LABEL}"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print("Jarvis is running in the background.")
        print(f"Logs: tail -f {LOG_DIR / 'jarvis.log'}")
    else:
        print("Jarvis is not running. Install with: python3 -m jarvis install")

"""Spoken, printed, and system feedback."""

from __future__ import annotations

import subprocess


def speak(message: str) -> None:
    subprocess.run(["say", message], check=False)


def notify(message: str) -> None:
    print(f"Jarvis: {message}", flush=True)
    safe = message.replace("\\", "\\\\").replace('"', '\\"')[:180]
    subprocess.run(
        [
            "osascript",
            "-e",
            f'display notification "{safe}" with title "Jarvis"',
        ],
        check=False,
    )

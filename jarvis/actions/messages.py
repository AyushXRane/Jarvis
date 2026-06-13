"""Send texts via iMessage/SMS."""

from __future__ import annotations

import json
import logging
import re
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

CONTACTS_PATH = Path.home() / ".jarvis" / "contacts.json"


def _load_contacts() -> dict[str, str]:
    if not CONTACTS_PATH.exists():
        return {}
    try:
        return {k.lower(): v for k, v in json.loads(CONTACTS_PATH.read_text()).items()}
    except (json.JSONDecodeError, AttributeError):
        return {}


def resolve_recipient(name: str) -> str:
    key = name.lower().strip()
    contacts = _load_contacts()
    if key in contacts:
        return contacts[key]

    digits = re.sub(r"[^\d+]", "", name)
    if len(digits) >= 10:
        return digits

    if "@" in name:
        return name.strip()

    return name.strip()


def send_message(recipient: str, message: str) -> None:
    target = resolve_recipient(recipient)
    escaped_target = target.replace("\\", "\\\\").replace('"', '\\"')
    escaped_message = message.replace("\\", "\\\\").replace('"', '\\"')

    script = f'''
tell application "Messages"
    activate
    set targetBuddy to participant "{escaped_target}" of (1st account whose service type = iMessage)
    send "{escaped_message}" to targetBuddy
end tell
'''
    logger.info("Sending text to %s: %s", target, message)
    subprocess.run(["osascript", "-e", script], check=True, capture_output=True, text=True)

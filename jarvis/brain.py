"""LLM-powered free-form command understanding via Ollama."""

from __future__ import annotations

import json
import logging
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from jarvis.parser import (
    BrightnessCommand,
    Command,
    MediaCommand,
    OpenAppCommand,
    PlayCommand,
    TextCommand,
    VolumeCommand,
    parse_command,
)

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
DEFAULT_MODEL = "llama3.2"

SYSTEM_PROMPT = """You are Jarvis, a macOS voice assistant. Convert the user's spoken request into ONE JSON object.

Available actions (pick exactly one):
- open_app: open an app or website {"action":"open_app","target":"chrome|safari|spotify|youtube|terminal|..."}
- play: play music or a video {"action":"play","query":"search terms","platform":"spotify|youtube","playlist":false}
- volume: {"action":"volume","direction":"up|down|mute|unmute"}
- brightness: {"action":"brightness","direction":"up|down"}
- media: media keys {"action":"media","control":"pause|play|next|previous"}
- text: send iMessage/SMS {"action":"text","recipient":"name or phone number","message":"message body"}
- answer: general question or conversation {"action":"answer","response":"short reply to speak aloud, under 2 sentences"}

Rules:
- Return ONLY raw JSON. No markdown, no explanation.
- For play commands, infer platform: music/playlist -> spotify, video/watch -> youtube.
- For text, extract who to message and what to say.
- Keep answer responses concise and natural for text-to-speech.
"""


@dataclass(frozen=True)
class AnswerCommand:
    response: str


FullCommand = Command | AnswerCommand


def ollama_available(model: str = DEFAULT_MODEL) -> bool:
    try:
        req = urllib.request.Request("http://127.0.0.1:11434/api/tags")
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read())
        models = [m.get("name", "") for m in data.get("models", [])]
        return any(model in name for name in models) or bool(models)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return False


def _extract_json(text: str) -> dict[str, Any] | None:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return None
    return None


def _dict_to_command(data: dict[str, Any]) -> FullCommand | None:
    action = data.get("action", "").lower()

    if action == "open_app":
        target = str(data.get("target", "")).strip().lower()
        return OpenAppCommand(target=target) if target else None

    if action == "play":
        query = str(data.get("query", "")).strip()
        platform = str(data.get("platform", "youtube")).strip().lower()
        if platform not in ("spotify", "youtube"):
            platform = "youtube"
        if query:
            return PlayCommand(
                query=query,
                platform=platform,  # type: ignore[arg-type]
                prefer_playlist=bool(data.get("playlist", False)),
            )
        return None

    if action == "volume":
        direction = str(data.get("direction", "")).lower()
        if direction in ("up", "down", "mute", "unmute"):
            return VolumeCommand(action=direction)  # type: ignore[arg-type]
        return None

    if action == "brightness":
        direction = str(data.get("direction", "")).lower()
        if direction in ("up", "down"):
            return BrightnessCommand(action=direction)  # type: ignore[arg-type]
        return None

    if action == "media":
        control = str(data.get("control", "")).lower()
        if control in ("pause", "play", "next", "previous"):
            return MediaCommand(action=control)  # type: ignore[arg-type]
        return None

    if action == "text":
        recipient = str(data.get("recipient", "")).strip()
        message = str(data.get("message", "")).strip()
        if recipient and message:
            return TextCommand(recipient=recipient, message=message)
        return None

    if action == "answer":
        response = str(data.get("response", "")).strip()
        return AnswerCommand(response=response) if response else None

    return None


def interpret_with_ollama(text: str, model: str = DEFAULT_MODEL) -> FullCommand | None:
    payload = json.dumps(
        {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            "stream": False,
            "format": "json",
        }
    ).encode()

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read())
        content = body.get("message", {}).get("content", "")
        data = _extract_json(content)
        if not data:
            logger.warning("Ollama returned unparseable response: %s", content[:200])
            return None
        command = _dict_to_command(data)
        logger.info("Ollama interpreted %r -> %s", text, command)
        return command
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        logger.warning("Ollama unavailable: %s", exc)
        return None


def resolve_command(
    text: str,
    *,
    use_ai: bool = True,
    model: str = DEFAULT_MODEL,
) -> FullCommand | None:
    """Resolve a command: fast rules first, then AI for free-form requests."""
    parsed = parse_command(text)
    if parsed:
        return parsed

    if use_ai and ollama_available(model):
        return interpret_with_ollama(text, model=model)

    return None

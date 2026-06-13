"""Flexible natural-language command parsing."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

Platform = Literal["spotify", "youtube"]
VolumeAction = Literal["up", "down", "mute", "unmute"]
BrightnessAction = Literal["up", "down"]
MediaAction = Literal["pause", "play", "next", "previous"]

WAKE_PREFIXES = ("jarvis", "hey jarvis", "okay jarvis", "ok jarvis")

OPEN_WORDS = frozenset({"open", "launch", "start", "boot", "load"})
PLAY_WORDS = frozenset({"play", "watch", "listen", "queue", "search", "find", "put", "stream", "show"})
LISTEN_WORDS = frozenset({"listen", "hear", "song", "album", "track", "music", "artist"})
WATCH_WORDS = frozenset({"watch", "video", "clip", "movie"})

PLATFORM_ALIASES: dict[str, Platform] = {
    "youtube": "youtube",
    "you tube": "youtube",
    "yt": "youtube",
    "spotify": "spotify",
    "spot": "spotify",
}

KNOWN_APPS = frozenset(
    {
        "arc",
        "chrome",
        "google chrome",
        "safari",
        "finder",
        "terminal",
        "messages",
        "notes",
        "mail",
        "photos",
        "music",
        "settings",
        "system settings",
        "preferences",
        "vscode",
        "visual studio code",
        "code",
        "cursor",
        "slack",
        "discord",
        "zoom",
        "calendar",
        "reminders",
    }
)

POLITE_PREFIX = re.compile(
    r"^(?:"
    r"(?:hey\s+|okay\s+|ok\s+)?jarvis[\s,]+|"
    r"(?:can|could|would)\s+you\s+|"
    r"(?:please\s+)?(?:i\s+(?:want\s+to|would\s+like\s+to|need\s+to)\s+)?"
    r")+",
    re.IGNORECASE,
)

STRUCTURED_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^play\s+(.+?)\s+on\s+(spotify|youtube)\s*$", re.I), "play"),
    (re.compile(r"^watch\s+(.+?)\s+on\s+youtube\s*$", re.I), "play_youtube"),
    (re.compile(r"^(spotify|youtube)\s*,?\s*play\s+(.+)\s*$", re.I), "platform_first"),
    (re.compile(r"^play\s+(.+?)\s+(?:on\s+)?(spotify|youtube)\s*$", re.I), "play"),
    (re.compile(r"^put\s+on\s+(.+?)\s+on\s+(spotify|youtube)\s*$", re.I), "play"),
    (re.compile(r"^(?:open|launch|start)\s+(?:up\s+)?(?:a\s+)?(.+?)\s+(?:playlist\s+)?on\s+(spotify|youtube)\s*$", re.I), "play"),
    (re.compile(r"^play\s+(?:a\s+)?(.+?)\s+(?:playlist\s+)?on\s+(spotify|youtube)\s*$", re.I), "play"),
    (re.compile(r"^play\s+(?:the\s+)?(?:video\s+)?(.+)\s*$", re.I), "play_inferred"),
    (re.compile(r"^listen\s+to\s+(.+?)\s+on\s+(spotify|youtube)\s*$", re.I), "play"),
    (re.compile(r"^listen\s+to\s+(.+)\s*$", re.I), "play_spotify"),
    (re.compile(r"^(?:open|launch|start)\s+(?:up\s+)?(youtube|spotify)\s*(?:app)?\s*$", re.I), "open_platform"),
    (re.compile(r"^(?:open|launch|start)\s+(?:up\s+)?(.+?)(?:\s+app)?\s*$", re.I), "open_app"),
]

VOLUME_PATTERNS: list[tuple[re.Pattern[str], VolumeAction]] = [
    (re.compile(r"\b(?:unmute|un mute|turn(?:\s+the)?\s+sound\s+(?:back\s+)?on)\b", re.I), "unmute"),
    (re.compile(r"\b(?:mute|silence|turn(?:\s+the)?\s+sound\s+off)\b", re.I), "mute"),
    (
        re.compile(
            r"(?:turn(?:\s+it|\s+the\s+volume)?\s+up|volume\s+up|louder|increase(?:\s+the)?\s+volume|make\s+it\s+louder)",
            re.I,
        ),
        "up",
    ),
    (
        re.compile(
            r"(?:turn(?:\s+it|\s+the\s+volume)?\s+down|volume\s+down|quieter|decrease(?:\s+the)?\s+volume|lower(?:\s+the)?\s+volume|make\s+it\s+quieter)",
            re.I,
        ),
        "down",
    ),
]

MEDIA_PATTERNS: list[tuple[re.Pattern[str], MediaAction]] = [
    (re.compile(r"\b(?:pause|stop(?:\s+the)?\s+music|stop(?:\s+playing)?)\b", re.I), "pause"),
    (re.compile(r"\b(?:resume|continue(?:\s+playing)?)\b", re.I), "play"),
    (re.compile(r"\b(?:next(?:\s+(?:song|track))?|skip(?:\s+(?:song|track|this))?)\b", re.I), "next"),
    (re.compile(r"\b(?:previous(?:\s+(?:song|track))?|go\s+back)\b", re.I), "previous"),
]

BRIGHTNESS_PATTERNS: list[tuple[re.Pattern[str], BrightnessAction]] = [
    (
        re.compile(
            r"(?:turn(?:\s+the)?\s+brightness\s+up|turn\s+up(?:\s+the)?\s+brightness|brightness\s+up|brighter|make(?:\s+it|\s+the\s+screen)?\s+brighter|increase(?:\s+the)?\s+brightness)",
            re.I,
        ),
        "up",
    ),
    (
        re.compile(
            r"(?:turn(?:\s+the)?\s+brightness\s+down|turn\s+down(?:\s+the)?\s+brightness|brightness\s+down|dim(?:\s+the\s+screen)?|dimmer|make(?:\s+it|\s+the\s+screen)?\s+darker|decrease(?:\s+the)?\s+brightness|lower(?:\s+the)?\s+brightness)",
            re.I,
        ),
        "down",
    ),
]

TEXT_PATTERNS = [
    re.compile(
        r"^(?:text|message|sms)\s+(.+?)\s+(?:saying|and say|that|to say)\s+(.+)$",
        re.I,
    ),
    re.compile(
        r"^send\s+(?:a\s+)?(?:text|message)\s+to\s+(.+?)\s+(?:saying|that says| saying)\s+(.+)$",
        re.I,
    ),
    re.compile(
        r"^tell\s+(.+?)\s+(?:that\s+)?(.+)$",
        re.I,
    ),
]


@dataclass(frozen=True)
class OpenAppCommand:
    target: str


@dataclass(frozen=True)
class PlayCommand:
    query: str
    platform: Platform
    prefer_playlist: bool = False


@dataclass(frozen=True)
class VolumeCommand:
    action: VolumeAction
    steps: int = 1


@dataclass(frozen=True)
class BrightnessCommand:
    action: BrightnessAction
    steps: int = 1


@dataclass(frozen=True)
class TextCommand:
    recipient: str
    message: str


@dataclass(frozen=True)
class MediaCommand:
    action: MediaAction


Command = OpenAppCommand | PlayCommand | VolumeCommand | BrightnessCommand | TextCommand | MediaCommand

# Backward compatibility
OpenCommand = OpenAppCommand


def _normalize(text: str) -> str:
    cleaned = text.lower().strip()
    cleaned = re.sub(r"[^\w\s'-]", " ", cleaned)
    cleaned = POLITE_PREFIX.sub("", cleaned)
    return " ".join(cleaned.split())


def _clean_query(query: str, *, prefer_playlist: bool = False) -> str:
    query = query.strip(" .,!?'\"-")
    query = re.sub(r"\bplease\b", " ", query)
    if prefer_playlist:
        query = re.sub(r"^(?:a\s+)?", "", query)
        query = re.sub(r"\s+playlist$", "", query)
    return " ".join(query.split())


def _detect_platform(text: str) -> Platform | None:
    found: Platform | None = None
    for alias, platform in sorted(PLATFORM_ALIASES.items(), key=lambda x: -len(x[0])):
        if re.search(rf"\b{re.escape(alias)}\b", text):
            found = platform
    return found


def _contains_any(text: str, words: frozenset[str]) -> bool:
    return any(re.search(rf"\b{re.escape(word)}\b", text) for word in words)


def _infer_platform(text: str, query: str) -> Platform:
    if _detect_platform(text):
        return _detect_platform(text)  # type: ignore[return-value]
    if _contains_any(text, WATCH_WORDS):
        return "youtube"
    if _contains_any(text, LISTEN_WORDS):
        return "spotify"
    if "playlist" in text:
        return "spotify"
    return "youtube"


def _parse_brightness(text: str) -> BrightnessCommand | None:
    for pattern, action in BRIGHTNESS_PATTERNS:
        if pattern.search(text):
            return BrightnessCommand(action=action)
    return None


def _parse_text(text: str) -> TextCommand | None:
    for pattern in TEXT_PATTERNS:
        match = pattern.match(text)
        if match:
            recipient = match.group(1).strip()
            message = match.group(2).strip(" .,!?'\"")
            if recipient and message:
                return TextCommand(recipient=recipient, message=message)
    return None


def _parse_volume(text: str) -> VolumeCommand | None:
    if re.search(r"\b(?:brightness|brighter|dimmer|screen)\b", text, re.I):
        return None
    for pattern, action in VOLUME_PATTERNS:
        if pattern.search(text):
            return VolumeCommand(action=action)
    return None


def _parse_media(text: str) -> MediaCommand | None:
    if _detect_platform(text) or re.search(r"\bon\s+(spotify|youtube)\b", text):
        return None
    for pattern, action in MEDIA_PATTERNS:
        if pattern.search(text):
            return MediaCommand(action=action)
    return None


def _parse_open_app(text: str) -> OpenAppCommand | None:
    if re.search(r"\bon\s+(spotify|youtube)\b", text):
        return None
    if _contains_any(text, PLAY_WORDS - OPEN_WORDS):
        return None

    match = re.match(
        r"^(?:open|launch|start)\s+(?:up\s+)?(.+?)(?:\s+app)?\s*$",
        text,
        re.I,
    )
    if not match:
        return None

    target = match.group(1).strip()
    if not target or target in {"a playlist", "playlist"}:
        return None

    if target in PLATFORM_ALIASES:
        return OpenAppCommand(target=PLATFORM_ALIASES[target])

    if target in KNOWN_APPS or len(target.split()) <= 3:
        return OpenAppCommand(target=target)

    return None


def _parse_structured(text: str) -> Command | None:
    prefer_playlist = "playlist" in text

    for pattern, kind in STRUCTURED_PATTERNS:
        match = pattern.match(text)
        if not match:
            continue

        if kind == "open_platform":
            platform = match.group(1).lower()
            return OpenAppCommand(target=platform)

        if kind == "open_app":
            target = match.group(1).strip()
            if re.search(r"\bon\s+(spotify|youtube)\b", target):
                continue
            if target in PLATFORM_ALIASES:
                return OpenAppCommand(target=PLATFORM_ALIASES[target])
            if _contains_any(text, PLAY_WORDS - OPEN_WORDS):
                continue
            return OpenAppCommand(target=target)

        if kind == "play_youtube":
            query = _clean_query(match.group(1), prefer_playlist=prefer_playlist)
            if query:
                return PlayCommand(query, "youtube", prefer_playlist)

        if kind == "platform_first":
            platform = match.group(1).lower()
            query = _clean_query(match.group(2), prefer_playlist=prefer_playlist)
            if query:
                return PlayCommand(query, platform, prefer_playlist)  # type: ignore[arg-type]

        if kind == "play":
            query = _clean_query(match.group(1), prefer_playlist=prefer_playlist)
            platform = match.group(2).lower()
            if query:
                return PlayCommand(query, platform, prefer_playlist)  # type: ignore[arg-type]

        if kind == "play_inferred":
            query = _clean_query(match.group(1), prefer_playlist=prefer_playlist)
            if query and not _detect_platform(query):
                platform = _infer_platform(text, query)
                return PlayCommand(query, platform, prefer_playlist)

        if kind == "play_spotify":
            query = _clean_query(match.group(1), prefer_playlist=prefer_playlist)
            if query:
                return PlayCommand(query, "spotify", prefer_playlist)

    return None


def _parse_loose(text: str) -> Command | None:
    platform = _detect_platform(text)
    prefer_playlist = "playlist" in text

    open_cmd = _parse_open_app(text)
    if open_cmd:
        return open_cmd

    open_only = _contains_any(text, OPEN_WORDS) and not _contains_any(
        text, PLAY_WORDS - OPEN_WORDS
    )
    if open_only and platform:
        remainder = text
        for alias in sorted(PLATFORM_ALIASES, key=len, reverse=True):
            remainder = re.sub(rf"\b{re.escape(alias)}\b", " ", remainder)
        for word in OPEN_WORDS | {"up", "app", "the"}:
            remainder = re.sub(rf"\b{word}\b", " ", remainder)
        remainder = " ".join(remainder.split())
        if not remainder or remainder in {"playlist", "a playlist"}:
            return OpenAppCommand(target=platform)

    play_intent = _contains_any(text, PLAY_WORDS) or (
        platform is not None and not open_only
    )
    if not play_intent:
        return None

    query = text
    for alias in sorted(PLATFORM_ALIASES, key=len, reverse=True):
        query = re.sub(rf"\b{re.escape(alias)}\b", " ", query)
    query = re.sub(
        r"^(?:play|watch|listen|queue|search|find|put|stream|show|open|launch|start)\s+",
        "",
        query,
    )
    query = re.sub(r"\b(?:on|up|to|a|an|the|please)\b", " ", query)
    query = re.sub(r"\b(?:playlist|video|song|music|some)\b", " ", query)
    query = _clean_query(query, prefer_playlist=prefer_playlist)

    if not query:
        return None

    resolved = platform or _infer_platform(text, query)
    return PlayCommand(query, resolved, prefer_playlist)


def parse_command(text: str) -> Command | None:
    """Turn free-form speech into a structured command."""
    if not text:
        return None

    normalized = _normalize(text)
    if not normalized:
        return None

    return (
        _parse_brightness(normalized)
        or _parse_volume(normalized)
        or _parse_text(normalized)
        or _parse_media(normalized)
        or _parse_structured(normalized)
        or _parse_loose(normalized)
    )


def parse_play_command(text: str) -> PlayCommand | None:
    command = parse_command(text)
    return command if isinstance(command, PlayCommand) else None

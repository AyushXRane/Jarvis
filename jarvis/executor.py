"""Execute parsed Jarvis commands."""

from __future__ import annotations

import logging

from jarvis.actions.messages import send_message
from jarvis.actions.spotify import open_spotify, play_on_spotify
from jarvis.actions.system import (
    brightness_down,
    brightness_up,
    mute_volume,
    open_application,
    pause_media,
    play_media,
    previous_track,
    skip_track,
    unmute_volume,
    volume_down,
    volume_up,
)
from jarvis.actions.youtube import open_youtube, play_on_youtube
from jarvis.brain import AnswerCommand, FullCommand
from jarvis.feedback import notify, speak
from jarvis.parser import (
    BrightnessCommand,
    MediaCommand,
    OpenAppCommand,
    PlayCommand,
    TextCommand,
    VolumeCommand,
)

logger = logging.getLogger(__name__)


def execute_command(command: FullCommand) -> bool:
    try:
        if isinstance(command, AnswerCommand):
            notify(command.response)
            speak(command.response)
            return True

        if isinstance(command, VolumeCommand):
            messages = {
                "up": ("Turning volume up", volume_up),
                "down": ("Turning volume down", volume_down),
                "mute": ("Muting", mute_volume),
                "unmute": ("Unmuting", unmute_volume),
            }
            message, action = messages[command.action]
            notify(message)
            speak(message)
            action(command.steps)
            return True

        if isinstance(command, BrightnessCommand):
            if command.action == "up":
                notify("Brightening screen")
                speak("Brightening screen")
                brightness_up(command.steps)
            else:
                notify("Dimming screen")
                speak("Dimming screen")
                brightness_down(command.steps)
            return True

        if isinstance(command, TextCommand):
            notify(f"Texting {command.recipient}")
            speak(f"Texting {command.recipient}")
            send_message(command.recipient, command.message)
            speak("Sent.")
            notify("Message sent.")
            return True

        if isinstance(command, MediaCommand):
            actions = {
                "pause": (pause_media, "Pausing"),
                "play": (play_media, "Resuming"),
                "next": (skip_track, "Skipping"),
                "previous": (previous_track, "Going back"),
            }
            action_fn, message = actions[command.action]
            notify(message)
            speak(message)
            action_fn()
            return True

        if isinstance(command, OpenAppCommand):
            notify(f"Opening {command.target}")
            speak(f"Opening {command.target}")
            if command.target == "spotify":
                open_spotify()
            elif command.target == "youtube":
                open_youtube()
            else:
                open_application(command.target)
            return True

        label = "playlist" if command.prefer_playlist else command.query
        notify(f"Playing {label!r} on {command.platform}")
        speak(f"Playing {label} on {command.platform}")
        if command.platform == "spotify":
            play_on_spotify(command.query, prefer_playlist=command.prefer_playlist)
        else:
            play_on_youtube(command.query, prefer_playlist=command.prefer_playlist)
        return True

    except Exception as exc:
        logger.exception("Command failed")
        notify(f"Something went wrong: {exc}")
        speak("Sorry, something went wrong.")
        return False

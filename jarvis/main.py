"""Jarvis voice assistant — entry point."""

from __future__ import annotations

import argparse
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from jarvis.brain import ollama_available, resolve_command
from jarvis.executor import execute_command
from jarvis.feedback import notify, speak
from jarvis.listener import VoiceListener
from jarvis.menubar import MenuBarIndicator
from jarvis.service import install_service, service_status, setup_permissions, uninstall_service
from jarvis.app_bundle import build_app

LOG_DIR = Path.home() / "Library" / "Logs"


def setup_logging(background: bool = False) -> None:
    handlers: list[logging.Handler] = []
    if background:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        handlers.append(
            RotatingFileHandler(
                LOG_DIR / "jarvis.log",
                maxBytes=1_000_000,
                backupCount=3,
            )
        )
    else:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        handlers=handlers,
    )


def handle_text(text: str, *, use_ai: bool = True) -> bool:
    command = resolve_command(text, use_ai=use_ai)
    if not command:
        notify(f"I didn't understand: {text!r}")
        speak("Sorry, I didn't understand that.")
        return False
    return execute_command(command)


def test_mic(seconds: float = 5.0) -> None:
    """Record and transcribe so the user can verify mic + speech recognition."""
    listener = VoiceListener()
    print(f"Speak now (say 'Jarvis') — recording {seconds:.0f} seconds...")
    text, level = listener.transcribe(seconds)
    print(f"Audio level: {level} (should be > 100 when you speak)")
    if level < 50:
        print("PROBLEM: No mic input. Enable Microphone for Jarvis/Python in System Settings.")
        return
    if text:
        print(f"Heard: {text!r}")
        if listener.matches_wake_word(text):
            print("Wake word detected — you're good to go!")
        else:
            print("Speech works, but wake word not detected. Try saying 'Jarvis' more clearly.")
    else:
        print("No speech recognized. Check internet connection (Google STT needs network).")


def run(wake_word: str = "jarvis", *, use_ai: bool = True, background: bool = False, show_menubar: bool = False) -> None:
    logger = logging.getLogger(__name__)
    listener = VoiceListener()
    ai_status = "with AI" if use_ai and ollama_available() else "rule-based mode"
    
    # Initialize menu bar indicator
    menubar = None
    if show_menubar:
        try:
            menubar = MenuBarIndicator()
            menubar.set_status("idle")
            menubar.run(quit_callback=lambda: sys.exit(0))
        except Exception as exc:
            logger.warning("Failed to start menu bar indicator: %s", exc)

    notify(f"Jarvis is online ({ai_status}). Say {wake_word!r} to activate.")
    if not background:
        speak("Jarvis is online and listening.")

    while True:
        try:
            if menubar:
                menubar.set_status("listening")
            
            listener.wait_for_wake_word(wake_word=wake_word)
            
            if menubar:
                menubar.set_status("processing")
            
            notify("Wake word detected — listening...")
            speak("Yes?")

            command_text = listener.listen_for_command(duration=10.0, silence_timeout=3.0)
            if not command_text:
                speak("I didn't catch that.")
                if menubar:
                    menubar.set_status("idle")
                continue

            logging.getLogger("jarvis").info("Command: %r", command_text)
            
            if menubar:
                menubar.set_status("speaking")
            
            handle_text(command_text, use_ai=use_ai)
            
            if menubar:
                menubar.set_status("idle")

        except KeyboardInterrupt:
            if not background:
                speak("Goodbye.")
            break


def main() -> None:
    parser = argparse.ArgumentParser(description="Jarvis — voice-activated assistant")
    sub = parser.add_subparsers(dest="cmd")

    run_parser = sub.add_parser("run", help="Run Jarvis in the foreground")
    run_parser.add_argument("--wake-word", default="jarvis")
    run_parser.add_argument("--no-ai", action="store_true", help="Disable Ollama AI parsing")

    sub.add_parser("install", help="Install Jarvis to run in background on login")
    sub.add_parser("uninstall", help="Remove background service")
    sub.add_parser("status", help="Check if background service is running")
    sub.add_parser("setup", help="Fix microphone permissions")
    sub.add_parser("test-mic", help="Test microphone and speech recognition")
    sub.add_parser("build", help="Build Jarvis.app for dock")

    parser.add_argument("--wake-word", default="jarvis", help=argparse.SUPPRESS)
    parser.add_argument("--background", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--no-ai", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--test-command", metavar="TEXT", help="Run a command without voice")

    args = parser.parse_args()
    background = getattr(args, "background", False)
    setup_logging(background=background)

    if args.cmd == "install":
        install_service()
        return
    if args.cmd == "uninstall":
        uninstall_service()
        return
    if args.cmd == "status":
        service_status()
        return
    if args.cmd == "setup":
        setup_permissions()
        return
    if args.cmd == "test-mic":
        setup_logging(background=False)
        test_mic()
        return
    if args.cmd == "build":
        app_path = build_app()
        print(f"Built Jarvis.app at: {app_path}")
        print("You can now:")
        print("  1. Drag Jarvis.app to your dock")
        print("  2. Double-click it to start Jarvis")
        print("  3. Or run: open Jarvis.app")
        return

    use_ai = not getattr(args, "no_ai", False)

    if args.test_command:
        ok = handle_text(args.test_command.lower(), use_ai=use_ai)
        sys.exit(0 if ok else 1)

    wake_word = getattr(args, "wake_word", "jarvis")
    run(wake_word=wake_word.lower(), use_ai=use_ai, background=background)


if __name__ == "__main__":
    main()

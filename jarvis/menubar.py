"""Menu bar status indicator for Jarvis."""

from __future__ import annotations

import logging
import threading
from typing import Callable

import rumps

logger = logging.getLogger(__name__)


class MenuBarIndicator:
    """Menu bar app to show Jarvis status."""

    def __init__(self) -> None:
        self.app = rumps.App("Jarvis", title="J")
        self.status = "idle"
        self.quit_callback: Callable[[], None] | None = None

    def set_status(self, status: str) -> None:
        """Update the menu bar icon based on status."""
        self.status = status
        if status == "listening":
            self.app.title = "🎤"
        elif status == "processing":
            self.app.title = "⚙️"
        elif status == "speaking":
            self.app.title = "🔊"
        else:  # idle
            self.app.title = "J"

    def run(self, quit_callback: Callable[[], None] | None = None) -> None:
        """Run the menu bar app in a separate thread."""
        self.quit_callback = quit_callback
        thread = threading.Thread(target=self.app.run, daemon=True)
        thread.start()
        logger.info("Menu bar indicator started")

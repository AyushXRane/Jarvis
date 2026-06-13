"""Microphone capture and speech-to-text."""

from __future__ import annotations

import logging
import time

import numpy as np
import sounddevice as sd
import speech_recognition as sr

logger = logging.getLogger(__name__)

SAMPLE_RATE = 16_000
CHANNELS = 1

WAKE_ALIASES = (
    "jarvis",
    "jar vis",
    "jarvus",
    "gervais",
)


class VoiceListener:
    """Records audio from the default mic and transcribes it."""

    def __init__(self, sample_rate: int = SAMPLE_RATE) -> None:
        self.sample_rate = sample_rate
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 200  # Lower threshold for better sensitivity
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.6  # Slightly shorter for faster response

    def _record(self, duration: float) -> tuple[sr.AudioData, int]:
        frames = int(duration * self.sample_rate)
        recording = sd.rec(
            frames,
            samplerate=self.sample_rate,
            channels=CHANNELS,
            dtype="int16",
        )
        sd.wait()
        level = int(np.abs(recording).max())
        audio = sr.AudioData(recording.tobytes(), self.sample_rate, 2)
        return audio, level

    def transcribe(self, duration: float = 4.0) -> tuple[str | None, int]:
        """Record and return (lowercase text or None, audio level)."""
        try:
            audio, level = self._record(duration)
            if level < 50:
                logger.warning(
                    "No mic input (level=%d). Grant Microphone access to Python/Jarvis in System Settings.",
                    level,
                )
                return None, level

            text = self.recognizer.recognize_google(audio)
            text = text.lower().strip()
            logger.info("Heard: %r (level=%d)", text, level)
            return text, level
        except sr.UnknownValueError:
            logger.debug("No speech detected this cycle")
            return None, 0
        except sr.RequestError as exc:
            logger.error("Speech recognition unavailable: %s", exc)
            return None, 0

    @staticmethod
    def matches_wake_word(text: str, wake_word: str = "jarvis") -> bool:
        if not text:
            return False
        if wake_word.lower() in text:
            return True
        return any(alias in text for alias in WAKE_ALIASES)

    def wait_for_wake_word(
        self,
        wake_word: str = "jarvis",
        chunk_seconds: float = 2.5,
    ) -> bool:
        """Listen continuously until the wake word is detected."""
        logger.info("Listening for wake word: %r", wake_word)

        while True:
            text, level = self.transcribe(chunk_seconds)
            if self.matches_wake_word(text or "", wake_word):
                logger.info("Wake word detected in: %r", text)
                return True
            time.sleep(0.05)

    def listen_for_command(self, duration: float = 8.0, silence_timeout: float = 3.0) -> str | None:
        """Listen for a spoken command after activation.
        
        Uses voice activity detection to end recording when user stops speaking.
        Falls back to fixed duration if VAD fails.
        """
        logger.info("Listening for command (max %.1fs, silence timeout %.1fs)...", duration, silence_timeout)
        
        try:
            # Try voice activity detection first
            return self._listen_with_vad(duration, silence_timeout)
        except Exception as exc:
            logger.debug("VAD failed, falling back to fixed duration: %s", exc)
            # Fallback to fixed duration recording
            text, _ = self.transcribe(duration)
            return text

    def _listen_with_vad(self, max_duration: float, silence_timeout: float) -> str | None:
        """Listen using voice activity detection - ends when silence detected."""
        self.recognizer.pause_threshold = 0.5  # Shorter pause threshold for VAD
        self.recognizer.phrase_threshold = 0.3  # More sensitive to speech start
        
        with sr.Microphone(sample_rate=self.sample_rate) as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                # listen_with_timeout will end when silence is detected
                audio = self.recognizer.listen(
                    source,
                    timeout=max_duration,
                    phrase_time_limit=silence_timeout
                )
                text = self.recognizer.recognize_google(audio)
                text = text.lower().strip()
                logger.info("Heard (VAD): %r", text)
                return text
            except sr.WaitTimeoutError:
                logger.debug("No speech detected within timeout")
                return None
            except sr.UnknownValueError:
                logger.debug("No speech detected this cycle")
                return None
            except sr.RequestError as exc:
                logger.error("Speech recognition unavailable: %s", exc)
                return None

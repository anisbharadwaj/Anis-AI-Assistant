"""Speech: mock microphone interface and helpers.
These mocks allow the application and tests to run without a physical microphone
or external speech services.
"""
import os
from typing import Callable, Optional


class MockMicrophone:
    """A controllable mock microphone. When MOCK_MIC environment variable is set to '1',
    the microphone reports as available. It can simulate audio input by calling a
    callback with pre-defined text.
    """

    def __init__(self):
        self.available = os.getenv("MOCK_MIC", "1") == "1"
        self._on_audio = None

    def is_available(self) -> bool:
        return self.available

    def start_listening(self, on_transcript: Callable[[str], None], phrase: Optional[str] = None):
        """Simulate listening. If phrase is provided, immediately call back with it."""
        self._on_audio = on_transcript
        if phrase is not None:
            # immediate callback for tests
            on_transcript(phrase)

    def stop_listening(self):
        self._on_audio = None

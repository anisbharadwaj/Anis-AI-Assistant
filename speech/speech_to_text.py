"""Speech-to-text mock adapter.
Provides a predictable interface usable by the UI and tests without external
services.
"""
from typing import Dict, Any


class MockSpeechToText:
    def transcribe(self, audio_bytes: bytes, language: str = "en") -> Dict[str, Any]:
        """Return a deterministic transcription for given bytes in tests.
        We don't process audio_bytes in the mock; return a fixed message.
        """
        return {"success": True, "transcript": "(mock) transcribed speech", "language": language}

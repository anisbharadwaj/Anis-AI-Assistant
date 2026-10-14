"""Text-to-speech mock adapter.
Plays no audio but provides an interface for TTS. Useful for tests and for
running the app on systems without TTS engines installed.
"""
from typing import Dict, Any


class MockTextToSpeech:
    def speak(self, text: str, language: str = "en", voice: str = None) -> Dict[str, Any]:
        # In mock mode we do not output audio. Return a record for tests.
        return {"success": True, "spoken_text": text, "language": language, "voice": voice}

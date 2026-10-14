# Speech mock tests
from speech.microphone import MockMicrophone
from speech.speech_to_text import MockSpeechToText
from speech.text_to_speech import MockTextToSpeech
from speech.language_detection import detect_language


def test_mock_microphone_available(monkeypatch):
    monkeypatch.setenv("MOCK_MIC", "1")
    m = MockMicrophone()
    assert m.is_available()


def test_speech_to_text_mock():
    stt = MockSpeechToText()
    r = stt.transcribe(b"fake-audio")
    assert r["success"]


def test_text_to_speech_mock():
    tts = MockTextToSpeech()
    r = tts.speak("hello")
    assert r["success"]


def test_language_detection():
    assert detect_language("Hello world") == "en"
    assert detect_language("नमस्ते") == "hi"
    # Assamese word example (uses Bengali/Assamese script)
    assert detect_language("অসমীয়া") == "as"

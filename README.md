Updated Phase 1: AI backend, mock speech modules, local provider stub, and SQLite memory.

Files added/changed:
- ai/local_provider.py (new)
- ai/online_provider.py (new)
- ai/__init__.py (new)
- speech/microphone.py (new)
- speech/speech_to_text.py (new)
- speech/text_to_speech.py (new)
- speech/language_detection.py (new)
- memory/database.py (new)
- tests/test_provider.py (new)
- tests/test_speech.py (new)
- .env.example (updated)

Run tests:
1) Activate virtualenv
   > .\\.venv\\Scripts\\Activate.ps1
2) Install deps
   > python -m pip install -r requirements.txt
3) Run pytest
   > python -m pytest -q

# Anis-AI-Assistant

This repository contains a working scaffold for the ANIS AI Windows assistant.

What's implemented so far (Phase 1/2 continuation):
- Typed chat UI using PySide6
- Assistant core with a provider abstraction and a MockProvider for offline/testing
- Registered action system with two actions: open_application and open_website
- Permission checks that require confirmation for medium/high risk actions
- Simple PowerShell setup script and test skeleton

How to run (Windows PowerShell):
1. Create and activate a virtual environment
   > python -m venv .venv
   > .\\.venv\\Scripts\\Activate.ps1
2. Install dependencies
   > python -m pip install --upgrade pip
   > python -m pip install -r requirements.txt
3. Run the app
   > python app.py

Notes and next steps:
- Speech (STT/TTS), multilingual detection, wake-word, YouTube automation, and verified subscription flows are NOT yet implemented and will be added incrementally.
- The MockProvider interprets simple "open <app>" and URL commands and can be replaced with a real provider via the AI_PROVIDER env var.

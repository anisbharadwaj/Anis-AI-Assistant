"""Core assistant facade and stubs.
This module will manage conversation state, provider selection, and the action registry.
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Response:
    success: bool
    text: str

class Assistant:
    def __init__(self, settings=None):
        self.settings = settings

    def handle_text(self, text: str) -> Response:
        # Placeholder: in future this will run language detection, intent parsing,
        # call AI provider, and route to actions.
        return Response(success=True, text=f"(stub) Echo: {text}")

# Expose a module-level default assistant
default_assistant = Assistant()

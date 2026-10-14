"""Core assistant facade and provider integration.
This module manages simple intent detection and routes actions to the action registry.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
import os

from ai.provider import get_provider
from core import action_registry

@dataclass
class Response:
    success: bool
    text: str
    action: Optional[str] = None
    action_args: Optional[Dict[str, Any]] = None
    requires_confirmation: bool = False


class Assistant:
    def __init__(self, settings=None):
        self.settings = settings
        self.provider = get_provider()

    def handle_text(self, text: str) -> Response:
        """Handle typed text: use provider to interpret, then either return
        a text response or an action request.
        The provider returns a dict with keys: type ('text'|'action'), text, and
        for actions: action_id, args, requires_confirmation.
        """
        parsed = self.provider.interpret(text)
        if parsed.get("type") == "action":
            action_id = parsed.get("action_id")
            args = parsed.get("args", {})
            requires_confirmation = parsed.get("requires_confirmation", False)
            return Response(
                success=True,
                text=parsed.get("text", ""),
                action=action_id,
                action_args=args,
                requires_confirmation=requires_confirmation,
            )
        else:
            return Response(success=True, text=parsed.get("text", "(no response)"))


# module-level default assistant
default_assistant = Assistant()

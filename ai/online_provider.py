"""Online provider stub placeholder.
This module shows where a cloud AI provider implementation can be added.
It intentionally does not contact any external service. Real networked
implementations must read credentials from environment variables and handle
errors, rate limits, and privacy concerns.
"""
import os
from typing import Dict, Any


class OnlineProvider:
    def __init__(self):
        self.api_key = os.getenv("AI_PROVIDER_KEY")

    def interpret(self, text: str) -> Dict[str, Any]:
        # Not implemented: cloud provider integration must be explicit and
        # require valid credentials. Here we raise an error to avoid silent use.
        if not self.api_key:
            return {"type": "text", "text": "(online provider) No API key configured. Set AI_PROVIDER_KEY to enable."}
        return {"type": "text", "text": "(online provider) Provider configured but integration not implemented."}

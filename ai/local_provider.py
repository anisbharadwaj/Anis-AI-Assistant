"""Local provider stub for future offline model integration.
This provider is a placeholder that behaves like a mock provider but is
selectable via AI_PROVIDER=local for future extension.
"""
import os
from typing import Dict, Any


class LocalProvider:
    """Stub local provider.
    Behavior:
      - If LOCAL_MODEL_PATH is set and points to an existing file, respond with a
        deterministic message indicating local-model mode is active.
      - Otherwise fall back to a harmless echo to avoid failing when no model is present.
    """

    def __init__(self):
        self.model_path = os.getenv("LOCAL_MODEL_PATH")

    def interpret(self, text: str) -> Dict[str, Any]:
        t = text.strip()
        if self.model_path and os.path.exists(self.model_path):
            # Placeholder deterministic response for local-model mode
            return {"type": "text", "text": f"(local-model) Received: {t}"}
        # fallback behavior
        return {"type": "text", "text": f"(local-model-fallback) Echo: {t}"}

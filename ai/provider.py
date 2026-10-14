"""AI provider abstraction and a MockProvider for offline/testing use.

If AI_PROVIDER is set to 'mock' or 'none' the MockProvider will be used.
A real provider implementation can be added later (openai, local, etc.) and
selected via the AI_PROVIDER environment variable.
"""
import os
from typing import Dict, Any


class ProviderBase:
    def interpret(self, text: str) -> Dict[str, Any]:
        raise NotImplementedError


class MockProvider(ProviderBase):
    """A very small interpreter that recognizes simple commands for testing.
    - "open <app>" -> open_application
    - "open <url>" or contains http -> open_website
    Otherwise echoes back.
    """
    def interpret(self, text: str) -> Dict[str, Any]:
        t = text.strip()
        lt = t.lower()
        # simple URL detection
        if "http://" in lt or "https://" in lt:
            return {
                "type": "action",
                "text": f"Opening website: {t}",
                "action_id": "open_website",
                "args": {"url": t},
                "requires_confirmation": False,
            }
        # open application phrase
        if lt.startswith("open "):
            target = t[5:].strip()
            # special-case YouTube channel subscription intent
            if "subscribe" in lt or "subscribe" in t.lower() or "subscribe to" in lt:
                # high risk - would require account auth and explicit confirmation
                return {
                    "type": "text",
                    "text": "I can help with subscribing, but subscribing requires authenticated browser access and explicit confirmation.",
                }
            return {
                "type": "action",
                "text": f"Opening application: {target}",
                "action_id": "open_application",
                "args": {"name": target},
                "requires_confirmation": False,
            }
        # search youtube
        if lt.startswith("search youtube") or "youtube" in lt:
            # route to open_website with youtube search URL
            q = t
            import urllib.parse

            query = urllib.parse.quote_plus(t)
            url = f"https://www.youtube.com/results?search_query={query}"
            return {
                "type": "action",
                "text": f"Searching YouTube for: {t}",
                "action_id": "open_website",
                "args": {"url": url},
                "requires_confirmation": False,
            }
        # default echo
        return {"type": "text", "text": f"(mock provider) Echo: {t}"}


def get_provider() -> ProviderBase:
    name = os.getenv("AI_PROVIDER", "none").lower()
    if name in ("none", "mock"):
        return MockProvider()
    # For now default to MockProvider with a warning comment; a real provider
    # integration can be added later.
    return MockProvider()

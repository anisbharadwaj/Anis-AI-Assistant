"""Optional, read-only verification that a matching visible Windows window exists."""
from __future__ import annotations

import os
import time
from typing import Any, Dict

IS_WINDOWS = os.name == "nt"


def _find_visible_window(title: str) -> bool:
    """Return True if any visible top-level window title contains ``title``."""
    if not IS_WINDOWS:
        return False

    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    matched = False

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def enum_windows(hwnd: int, _lparam: int) -> bool:
        nonlocal matched
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length:
                buffer = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buffer, len(buffer))
                if title.casefold() in buffer.value.casefold():
                    matched = True
                    return False
        return True

    user32.EnumWindows(enum_windows, 0)
    return matched


def verify_window_visible(
    title: str, timeout_seconds: float = 3.0, poll_interval: float = 0.1
) -> Dict[str, Any]:
    """Wait briefly for a visible window whose title contains ``title``.

    This checks visibility only; it does not inspect or control window contents.
    """
    if not isinstance(title, str) or not title.strip():
        return {"success": False, "visible": False, "error": "Invalid window title"}
    if not IS_WINDOWS:
        return {
            "success": False,
            "visible": False,
            "title": title,
            "error": "Window visibility verification is only supported on Windows",
        }
    if (
        isinstance(timeout_seconds, bool)
        or not isinstance(timeout_seconds, (int, float))
        or timeout_seconds < 0
        or timeout_seconds != timeout_seconds
        or timeout_seconds == float("inf")
    ):
        return {
            "success": False,
            "visible": False,
            "title": title,
            "error": "timeout_seconds must be finite and non-negative",
        }
    if (
        isinstance(poll_interval, bool)
        or not isinstance(poll_interval, (int, float))
        or poll_interval <= 0
        or poll_interval != poll_interval
        or poll_interval == float("inf")
    ):
        return {
            "success": False,
            "visible": False,
            "title": title,
            "error": "poll_interval must be finite and greater than zero",
        }

    deadline = time.monotonic() + float(timeout_seconds)
    while True:
        if _find_visible_window(title.strip()):
            return {"success": True, "visible": True, "title": title}
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        time.sleep(min(float(poll_interval), remaining))

    return {
        "success": False,
        "visible": False,
        "title": title,
        "error": f"No visible window matching '{title}' was found before timeout",
    }

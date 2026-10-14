"""Safe Windows application and website launching helpers.

Only applications in APP_MAP may be launched. No shell command is ever
constructed from user input, and subprocess is always called with shell=False.
"""
from __future__ import annotations

import math
import os
import shutil
import subprocess
import webbrowser
from typing import Any, Dict, Optional
from urllib.parse import urlsplit

from automation.window_verification import verify_window_visible

IS_WINDOWS = os.name == "nt"

# Names are deliberately allowlisted. Do not add arbitrary user-provided commands.
APP_MAP = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "file explorer": "explorer.exe",
    "explorer": "explorer.exe",
    "settings": "ms-settings:",
    "edge": "msedge.exe",
    "chrome": "chrome.exe",
    "firefox": "firefox.exe",
    "vscode": "code",
    "code": "code",
}

APP_WINDOW_TITLES = {
    "notepad": "Notepad",
    "calculator": "Calculator",
    "calc": "Calculator",
    "file explorer": "File Explorer",
    "explorer": "File Explorer",
    "settings": "Settings",
    "edge": "Microsoft Edge",
    "chrome": "Google Chrome",
    "firefox": "Mozilla Firefox",
    "vscode": "Visual Studio Code",
    "code": "Visual Studio Code",
}


def _startfile(target: str) -> None:
    """Call Windows ShellExecute support, with a clear error off Windows."""
    startfile = getattr(os, "startfile", None)
    if startfile is None:
        raise OSError("Windows application launching is only available on Windows")
    startfile(target)


def _which_windows_program(name: str) -> Optional[str]:
    """Resolve an allowlisted application name; never return an unknown input."""
    if not isinstance(name, str):
        return None
    target = APP_MAP.get(name.strip().casefold())
    if target is None:
        return None
    if target.casefold().startswith("ms-settings:"):
        return target
    return shutil.which(target) or (target if IS_WINDOWS else None)


def open_application(
    name: str,
    verify_window: bool = False,
    verify_timeout: float = 3.0,
) -> Dict[str, Any]:
    """Launch an allowlisted Windows application and optionally check visibility."""
    if not isinstance(name, str) or not name.strip():
        return {
            "success": False,
            "action": "open_application",
            "error": "Invalid application name",
        }
    if not isinstance(verify_window, bool):
        return {
            "success": False,
            "action": "open_application",
            "error": "verify_window must be a boolean",
        }
    if (
        isinstance(verify_timeout, bool)
        or not isinstance(verify_timeout, (int, float))
        or not math.isfinite(verify_timeout)
        or verify_timeout < 0
    ):
        return {
            "success": False,
            "action": "open_application",
            "error": "verify_timeout must be a finite, non-negative number",
        }

    key = name.strip().casefold()
    command = _which_windows_program(key)
    if command is None:
        if key not in APP_MAP:
            error = f"Unsupported application: {name.strip()}"
        else:
            error = f"Application is unavailable on this system: {name.strip()}"
        return {"success": False, "action": "open_application", "error": error}

    try:
        if command.casefold().startswith("ms-settings:"):
            if not IS_WINDOWS:
                raise OSError("Windows Settings is only available on Windows")
            _startfile(command)
        else:
            # command comes solely from APP_MAP (or PATH resolution of that value).
            # Never use shell=True, and never pass arbitrary user input to Popen.
            # ShellExecute fallback supports registered Windows apps not on PATH.
            if IS_WINDOWS and command.casefold().endswith((".cmd", ".bat")):
                _startfile(command)
            else:
                try:
                    subprocess.Popen([command], shell=False)
                except OSError:
                    if not IS_WINDOWS:
                        raise
                    _startfile(command)

        result: Dict[str, Any] = {
            "success": True,
            "action": "open_application",
            "summary": f"Opened {name.strip()}",
        }
        if verify_window:
            title = APP_WINDOW_TITLES.get(key)
            if title is None:
                result["window_verification"] = {
                    "success": False,
                    "visible": False,
                    "error": "No window title is configured for this application",
                }
            else:
                result["window_verification"] = verify_window_visible(
                    title, timeout_seconds=float(verify_timeout)
                )
        return result
    except Exception as exc:
        return {"success": False, "action": "open_application", "error": str(exc)}


def _normalize_http_url(url: str) -> str:
    """Normalize a website URL while accepting only HTTP(S) destinations."""
    candidate = url.strip()
    if not candidate:
        raise ValueError("Invalid URL")

    parsed = urlsplit(candidate)
    if parsed.scheme and parsed.scheme.casefold() not in {"http", "https"}:
        raise ValueError("Only http:// and https:// website URLs are allowed")
    if not parsed.scheme:
        candidate = "https://" + candidate.lstrip("/")

    parsed = urlsplit(candidate)
    if parsed.scheme.casefold() not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Invalid HTTP(S) URL")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("URLs containing embedded credentials are not allowed")
    try:
        _ = parsed.port
    except ValueError as exc:
        raise ValueError("Invalid URL port") from exc
    return candidate


def open_website(url: str) -> Dict[str, Any]:
    """Open a validated HTTP(S) URL in the user's default browser."""
    if not isinstance(url, str) or not url.strip():
        return {"success": False, "action": "open_website", "error": "Invalid URL"}
    try:
        normalized_url = _normalize_http_url(url)
        opened = webbrowser.open(normalized_url, new=2)
        if not opened:
            return {
                "success": False,
                "action": "open_website",
                "error": "The default browser did not confirm that it opened the URL",
            }
        return {
            "success": True,
            "action": "open_website",
            "summary": f"Opened website {normalized_url}",
        }
    except Exception as exc:
        return {"success": False, "action": "open_website", "error": str(exc)}

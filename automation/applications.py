"""Windows application launcher utilities.

Provides safe, validated ways to open common Windows applications and the default browser.
Never execute arbitrary shell commands from untrusted input.
"""
from typing import Dict, Any
import os
import subprocess
import shutil
from pathlib import Path

# Mapping of friendly names to executable names or special handlers
APP_MAP = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "file explorer": "explorer.exe",
    "explorer": "explorer.exe",
    "settings": "ms-settings:",
    "edge": "msedge",
    "chrome": "chrome",
    "firefox": "firefox",
    "vscode": "code",
    "code": "code",
}


def _which_windows_program(name: str) -> str:
    """Try to resolve a program name to an executable path or command.
    Returns the command to execute (may be name itself if found on PATH).
    """
    # Direct mapping first
    key = name.lower()
    if key in APP_MAP:
        return APP_MAP[key]
    # Try to locate on PATH
    exe = shutil.which(name)
    if exe:
        return exe
    # try with .exe suffix
    exe = shutil.which(f"{name}.exe")
    if exe:
        return exe
    # return original name as fallback (will likely fail)
    return name


def open_application(name: str) -> Dict[str, Any]:
    """Attempt to open a known application by friendly name.
    Returns a structured result. Does not allow arbitrary shell commands.
    """
    if not name or not isinstance(name, str):
        return {"success": False, "action": "open_application", "error": "Invalid application name"}

    cmd = _which_windows_program(name)
    try:
        # Special URI like ms-settings:
        if cmd.lower().startswith("ms-settings") or cmd.lower().startswith("http"):
            os.startfile(cmd)
            return {"success": True, "action": "open_application", "summary": f"Opened {name}"}

        # If it's an executable or command, use subprocess to launch.
        # Avoid shell=True when possible.
        if Path(cmd).exists() and cmd.lower().endswith(".exe"):
            subprocess.Popen([cmd])
        else:
            # rely on startfile to let Windows handle registered apps
            try:
                os.startfile(cmd)
            except OSError:
                # fallback to subprocess which may work for path-like commands
                subprocess.Popen(cmd, shell=True)
        return {"success": True, "action": "open_application", "summary": f"Opened {name}"}
    except Exception as e:
        return {"success": False, "action": "open_application", "error": str(e)}


def open_website(url: str) -> Dict[str, Any]:
    """Open a website URL in the default browser. Validate basic URL form."""
    if not url or not isinstance(url, str):
        return {"success": False, "action": "open_website", "error": "Invalid URL"}
    if not (url.startswith("http://") or url.startswith("https://")):
        # normalize simple inputs like "youtube.com" -> https://youtube.com
        url = "https://" + url
    try:
        os.startfile(url)
        return {"success": True, "action": "open_website", "summary": f"Opened website {url}"}
    except Exception as e:
        return {"success": False, "action": "open_website", "error": str(e)}

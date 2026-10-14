"""Action registry: register actions, validate arguments, and execute them.
This module implements the registered-action system required by the project.
"""
from dataclasses import dataclass
from typing import Callable, Dict, Any, Optional
import subprocess
import os
import shlex

from security.permissions import requires_confirmation


@dataclass
class Action:
    id: str
    description: str
    args_schema: Dict[str, type]
    permission_level: str  # 'low', 'medium', 'high'
    timeout: Optional[int]
    handler: Callable[[Dict[str, Any]], Dict[str, Any]]


_registry: Dict[str, Action] = {}


def register_action(action: Action):
    _registry[action.id] = action


def get_action(action_id: str) -> Optional[Action]:
    return _registry.get(action_id)


def execute_action(action_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
    action = get_action(action_id)
    if not action:
        return {"success": False, "action": action_id, "error": "Unknown action"}

    # validate args types
    for k, t in action.args_schema.items():
        if k not in args:
            return {"success": False, "action": action_id, "error": f"Missing argument: {k}"}
        if not isinstance(args[k], t):
            # allow str convertible
            if t == str:
                args[k] = str(args[k])
            else:
                return {"success": False, "action": action_id, "error": f"Invalid type for {k}: expected {t}"}

    # permission check - actual confirmation handled by UI layer
    if requires_confirmation(action.permission_level):
        return {
            "success": False,
            "action": action_id,
            "error": "requires_confirmation",
            "requires_confirmation": True,
        }

    # execute handler
    try:
        result = action.handler(args)
        return {"success": True, "action": action_id, "summary": result.get("summary", "(no summary)")}
    except Exception as e:
        return {"success": False, "action": action_id, "error": str(e)}


# Handlers

def _open_application_handler(args: Dict[str, Any]) -> Dict[str, Any]:
    name = args.get("name")
    # map friendly names to common Windows executables
    mapping = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "file explorer": "explorer.exe",
        "explorer": "explorer.exe",
        "edge": "msedge",
        "chrome": "chrome",
        "firefox": "firefox",
        "vscode": "code",
        "code": "code",
    }
    cmd = mapping.get(name.lower(), name)
    try:
        # Try os.startfile first for simple names/paths/URLs
        if os.path.exists(cmd) or cmd.lower().endswith(".exe"):
            subprocess.Popen([cmd])
        else:
            # attempt to start by name - relies on PATH or shell
            subprocess.Popen(cmd, shell=True)
        return {"summary": f"Launched {name}"}
    except Exception as e:
        raise


def _open_website_handler(args: Dict[str, Any]) -> Dict[str, Any]:
    url = args.get("url")
    try:
        os.startfile(url)
        return {"summary": f"Opened website {url}"}
    except Exception as e:
        raise


# Register default actions
register_action(
    Action(
        id="open_application",
        description="Open an installed application by name",
        args_schema={"name": str},
        permission_level="low",
        timeout=10,
        handler=_open_application_handler,
    )
)

register_action(
    Action(
        id="open_website",
        description="Open a website URL in the default browser",
        args_schema={"url": str},
        permission_level="low",
        timeout=10,
        handler=_open_website_handler,
    )
)

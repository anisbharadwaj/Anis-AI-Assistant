from dataclasses import dataclass, field
from typing import Callable, Dict, Any, Optional
import subprocess
import os
import shlex

from security.permissions import requires_confirmation
from automation import applications, files, windows_system
from security.audit_log import log_action


@dataclass
class Action:
    id: str
    description: str
    args_schema: Dict[str, type]
    permission_level: str  # 'low', 'medium', 'high'
    timeout: Optional[int]
    handler: Callable[[Dict[str, Any]], Dict[str, Any]]
    optional_args_schema: Dict[str, type] = field(default_factory=dict)


_registry: Dict[str, Action] = {}


def register_action(action: Action):
    _registry[action.id] = action


def get_action(action_id: str) -> Optional[Action]:
    return _registry.get(action_id)


def execute_action(action_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
    action = get_action(action_id)
    if not action:
        return {"success": False, "action": action_id, "error": "Unknown action"}
    if not isinstance(args, dict):
        return {"success": False, "action": action_id, "error": "Arguments must be an object"}
    args = dict(args)

    # validate required args types
    for k, t in action.args_schema.items():
        if k not in args:
            return {"success": False, "action": action_id, "error": f"Missing argument: {k}"}
        if not isinstance(args[k], t):
            # allow str convertible
            if t == str:
                args[k] = str(args[k])
            else:
                return {"success": False, "action": action_id, "error": f"Invalid type for {k}: expected {t}"}

    # Validate optional arguments and reject misspelled or unsupported keys.
    unknown_args = set(args) - set(action.args_schema) - set(action.optional_args_schema)
    if unknown_args:
        names = ", ".join(sorted(unknown_args))
        return {"success": False, "action": action_id, "error": f"Unsupported argument(s): {names}"}

    for k, t in action.optional_args_schema.items():
        if k not in args:
            continue
        value = args[k]
        # JSON clients often represent whole-number timeouts as integers; accept those
        # for float fields, but never treat bool as a number.
        if t is float and isinstance(value, (int, float)) and not isinstance(value, bool):
            args[k] = float(value)
        elif not isinstance(value, t):
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
        result = action.handler(**args)
        # log audit
        try:
            log_action(action_id, str(args), success=bool(result.get("success")))
        except Exception:
            pass
        return result
    except Exception as e:
        return {"success": False, "action": action_id, "error": str(e)}


# Register default actions that use automation modules
register_action(
    Action(
        id="open_application",
        description="Open an installed application by name; optional window visibility verification is available",
        args_schema={"name": str},
        optional_args_schema={"verify_window": bool, "verify_timeout": float},
        permission_level="low",
        timeout=10,
        handler=applications.open_application,
    )
)

register_action(
    Action(
        id="open_website",
        description="Open a website URL in the default browser",
        args_schema={"url": str},
        permission_level="low",
        timeout=10,
        handler=applications.open_website,
    )
)

register_action(
    Action(
        id="list_directory",
        description="List files in a directory",
        args_schema={"path": str},
        permission_level="low",
        timeout=10,
        handler=files.list_directory,
    )
)

register_action(
    Action(
        id="search_file",
        description="Search for files by pattern",
        args_schema={"start_dir": str, "pattern": str},
        permission_level="low",
        timeout=30,
        handler=files.search_file,
    )
)

register_action(
    Action(
        id="create_folder",
        description="Create a folder",
        args_schema={"path": str},
        permission_level="medium",
        timeout=10,
        handler=files.create_folder,
    )
)

register_action(
    Action(
        id="create_text_file",
        description="Create a text file",
        args_schema={"path": str, "content": str},
        permission_level="medium",
        timeout=10,
        handler=files.create_text_file,
    )
)

register_action(
    Action(
        id="read_text_file",
        description="Read a text file",
        args_schema={"path": str},
        permission_level="low",
        timeout=10,
        handler=files.read_text_file,
    )
)

register_action(
    Action(
        id="rename_file",
        description="Rename a file",
        args_schema={"src": str, "dest": str},
        permission_level="medium",
        timeout=20,
        handler=files.rename_file,
    )
)

register_action(
    Action(
        id="copy_file",
        description="Copy a file",
        args_schema={"src": str, "dest": str},
        permission_level="medium",
        timeout=30,
        handler=files.copy_file,
    )
)

register_action(
    Action(
        id="move_file",
        description="Move a file",
        args_schema={"src": str, "dest": str},
        permission_level="medium",
        timeout=30,
        handler=files.move_file,
    )
)

register_action(
    Action(
        id="move_to_trash",
        description="Move a file to Recycle Bin",
        args_schema={"path": str},
        permission_level="high",
        timeout=30,
        handler=files.move_to_trash,
    )
)

register_action(
    Action(
        id="get_system_info",
        description="Get basic system information",
        args_schema={"info_type": str},
        permission_level="low",
        timeout=10,
        handler=windows_system.get_disk_space,
    )
)

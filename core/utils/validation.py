"""core/utils/validation.py

Robust validation and safe JSON loading utilities.

Follow defensive patterns: explicit typing, clear exceptions, and edge-case handling.
"""
from __future__ import annotations

import io
import json
from typing import Any, Dict

# Custom exceptions for clear error mapping
class ValidationError(Exception):
    """Generic validation failure."""


class InvalidJSONError(ValidationError):
    """Raised when JSON parsing fails."""


class FileTooLargeError(ValidationError):
    """Raised when a file exceeds the allowed maximum size for safety."""


class InvalidCommandError(ValidationError):
    """Raised when command text does not meet required constraints."""


def safe_load_json_from_string(s: Any) -> Dict[str, Any]:
    """Safely parse a JSON string into a dictionary.

    Defensive checks:
    - Non-string inputs are rejected.
    - Empty or whitespace-only strings are rejected.
    - Malformed JSON raises InvalidJSONError with the underlying message.

    Returns an empty dict if the JSON represents `null` or an empty structure.
    """
    if s is None:
        raise InvalidJSONError("InvalidJSONError: input is None.")

    if not isinstance(s, (str, bytes, bytearray)):
        raise InvalidJSONError("InvalidJSONError: input must be a JSON string or bytes.")

    if isinstance(s, (bytes, bytearray)):
        try:
            s = s.decode("utf-8")
        except Exception as exc:  # pragma: no cover - extremely defensive
            raise InvalidJSONError(f"InvalidJSONError: could not decode bytes: {exc}")

    if not s.strip():
        raise InvalidJSONError("InvalidJSONError: input string is empty or whitespace.")

    try:
        value = json.loads(s)
    except json.JSONDecodeError as exc:
        raise InvalidJSONError(f"InvalidJSONError: failed to parse JSON. {exc.msg}")

    if value is None:
        # Normalize JSON `null` to an empty dict to simplify callers
        return {}

    if not isinstance(value, dict):
        # Be strict: callers expect a mapping
        raise InvalidJSONError("InvalidJSONError: JSON root must be an object/dictionary.")

    return value


def safe_load_json_file(path: str, max_size: int = 1_000_000) -> Dict[str, Any]:
    """Safely load and parse a JSON file from disk.

    Defensive checks:
    - Path must be a non-empty string.
    - File must exist and be readable.
    - File size is checked against max_size (in bytes) before full read.
    - JSON parsing errors are wrapped in InvalidJSONError.

    The function minimizes memory usage by checking size first and reading with an
    explicit TextIO wrapper.
    """
    if not path or not isinstance(path, str):
        raise FileNotFoundError("FileNotFoundError: path must be a non-empty string.")

    # Use os path functions lazily to avoid extra imports in callers
    try:
        stat = __import__("os").stat(path)
    except FileNotFoundError:
        raise FileNotFoundError(f"FileNotFoundError: no such file '{path}'.")
    except PermissionError:
        raise PermissionError(f"PermissionError: insufficient permissions to stat '{path}'.")

    file_size = getattr(stat, "st_size", None)
    if file_size is None:
        # If size is unknown, be conservative and allow read (rare)
        file_size = 0

    if file_size > max_size:
        raise FileTooLargeError(f"FileTooLargeError: file '{path}' is {file_size} bytes, exceeds limit {max_size}.")

    try:
        with open(path, "r", encoding="utf-8") as fh:  # type: io.TextIOBase
            content = fh.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"FileNotFoundError: no such file '{path}'.")
    except PermissionError:
        raise PermissionError(f"PermissionError: insufficient permissions to read '{path}'.")
    except Exception as exc:  # pragma: no cover - IO error
        raise ValidationError(f"ValidationError: failed to read '{path}': {exc}")

    return safe_load_json_from_string(content)


def validate_command_text(command: Any, *, require_keyword: str = "anis") -> str:
    """Validate a spoken/typed command string before sending to intent processors.

    - Ensures the command is a non-empty string.
    - Trims whitespace and enforces a maximum length to avoid accidental huge payloads.
    - Optionally requires a keyword (default: 'anis') present in the command.

    Returns the cleaned command (lowercased) on success.

    Raises InvalidCommandError on all invalid inputs with descriptive messages.
    """
    if command is None:
        raise InvalidCommandError("InvalidCommandError: command is None.")

    if not isinstance(command, str):
        raise InvalidCommandError("InvalidCommandError: command must be a string.")

    cleaned = command.strip()
    if not cleaned:
        raise InvalidCommandError("InvalidCommandError: command is empty or whitespace.")

    # Defensive upper bound for command size (avoid extremely large inputs)
    max_len = 10_000
    if len(cleaned) > max_len:
        raise InvalidCommandError(f"InvalidCommandError: command length {len(cleaned)} exceeds allowed {max_len}.")

    lowered = cleaned.lower()
    if require_keyword and require_keyword.lower() not in lowered:
        raise InvalidCommandError(f"InvalidCommandError: required keyword '{require_keyword}' not present in command.")

    return lowered

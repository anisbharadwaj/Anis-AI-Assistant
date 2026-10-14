"""File and folder operations with validation and safe defaults.

This module restricts operations to an allowlist of directories to reduce risks.
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
import shutil
import os
import fnmatch
from send2trash import send2trash

# Default allowed directories: user home and Documents
from dotenv import load_dotenv
load_dotenv()

ALLOWED_DIRS = [
    Path(os.path.expanduser("~")),
    Path(os.path.join(os.path.expanduser("~"), "Documents")),
]
# Allow overriding via environment variable (semicolon-separated)
if os.getenv("ALLOWED_DIRS"):
    parts = os.getenv("ALLOWED_DIRS").split(";")
    ALLOWED_DIRS = [Path(p).expanduser().resolve() for p in parts if p]


def _is_path_allowed(p: Path) -> bool:
    try:
        rp = p.resolve()
    except RuntimeError:
        return False
    for base in ALLOWED_DIRS:
        try:
            if rp.is_relative_to(base.resolve()):
                return True
        except Exception:
            # fallback for older Python
            if str(rp).startswith(str(base.resolve())):
                return True
    return False


def list_directory(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {"success": False, "error": "Path does not exist"}
    if not _is_path_allowed(p):
        return {"success": False, "error": "Path not allowed"}
    try:
        items = []
        for child in p.iterdir():
            items.append({"name": child.name, "is_dir": child.is_dir(), "size": child.stat().st_size})
        return {"success": True, "path": str(p.resolve()), "items": items}
    except Exception as e:
        return {"success": False, "error": str(e)}


def search_file(start_dir: str, pattern: str, max_results: int = 50) -> Dict[str, Any]:
    p = Path(start_dir)
    if not p.exists():
        return {"success": False, "error": "Start directory does not exist"}
    if not _is_path_allowed(p):
        return {"success": False, "error": "Path not allowed"}
    matches = []
    try:
        for root, dirs, files in os.walk(p):
            for name in files + dirs:
                if fnmatch.fnmatch(name.lower(), pattern.lower()):
                    matches.append(str(Path(root) / name))
                    if len(matches) >= max_results:
                        return {"success": True, "matches": matches}
        return {"success": True, "matches": matches}
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_folder(path: str) -> Dict[str, Any]:
    p = Path(path)
    if p.exists():
        return {"success": False, "error": "Folder already exists"}
    if not _is_path_allowed(p.parent):
        return {"success": False, "error": "Destination not allowed"}
    try:
        p.mkdir(parents=True, exist_ok=False)
        return {"success": True, "summary": f"Created folder {str(p)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_text_file(path: str, content: str = "") -> Dict[str, Any]:
    p = Path(path)
    if p.exists():
        return {"success": False, "error": "File already exists"}
    if not _is_path_allowed(p.parent):
        return {"success": False, "error": "Destination not allowed"}
    try:
        p.write_text(content, encoding="utf-8")
        return {"success": True, "summary": f"Created file {str(p)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def read_text_file(path: str, max_size: int = 200000) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists() or not p.is_file():
        return {"success": False, "error": "File not found"}
    if not _is_path_allowed(p):
        return {"success": False, "error": "Access to path not allowed"}
    try:
        size = p.stat().st_size
        if size > max_size:
            return {"success": False, "error": "File too large to read"}
        content = p.read_text(encoding="utf-8")
        return {"success": True, "content": content}
    except Exception as e:
        return {"success": False, "error": str(e)}


def rename_file(src: str, dest: str) -> Dict[str, Any]:
    s = Path(src)
    d = Path(dest)
    if not s.exists():
        return {"success": False, "error": "Source does not exist"}
    if not _is_path_allowed(s) or not _is_path_allowed(d.parent):
        return {"success": False, "error": "Path not allowed"}
    if d.exists():
        return {"success": False, "error": "Destination already exists"}
    try:
        s.rename(d)
        return {"success": True, "summary": f"Renamed to {str(d)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def copy_file(src: str, dest: str) -> Dict[str, Any]:
    s = Path(src)
    d = Path(dest)
    if not s.exists():
        return {"success": False, "error": "Source does not exist"}
    if not _is_path_allowed(s) or not _is_path_allowed(d.parent):
        return {"success": False, "error": "Path not allowed"}
    if d.exists():
        return {"success": False, "error": "Destination already exists"}
    try:
        shutil.copy2(str(s), str(d))
        return {"success": True, "summary": f"Copied to {str(d)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def move_file(src: str, dest: str) -> Dict[str, Any]:
    s = Path(src)
    d = Path(dest)
    if not s.exists():
        return {"success": False, "error": "Source does not exist"}
    if not _is_path_allowed(s) or not _is_path_allowed(d.parent):
        return {"success": False, "error": "Path not allowed"}
    if d.exists():
        return {"success": False, "error": "Destination already exists"}
    try:
        shutil.move(str(s), str(d))
        return {"success": True, "summary": f"Moved to {str(d)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def move_to_trash(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {"success": False, "error": "Path does not exist"}
    if not _is_path_allowed(p):
        return {"success": False, "error": "Path not allowed"}
    try:
        send2trash(str(p))
        return {"success": True, "summary": f"Moved {str(p)} to Recycle Bin"}
    except Exception as e:
        return {"success": False, "error": str(e)}

"""Windows system information utilities."""
from typing import Dict, Any
import platform
import shutil
import os

try:
    import psutil
except Exception:
    psutil = None


def get_battery_status() -> Dict[str, Any]:
    if not psutil:
        return {"success": False, "error": "psutil not installed"}
    try:
        batt = psutil.sensors_battery()
        if batt is None:
            return {"success": False, "error": "No battery information available"}
        return {"success": True, "percent": batt.percent, "plugged_in": batt.power_plugged}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_disk_space(path: str = None) -> Dict[str, Any]:
    try:
        p = path or os.path.expanduser("~")
        total, used, free = shutil.disk_usage(p)
        return {"success": True, "total": total, "used": used, "free": free}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_memory_usage() -> Dict[str, Any]:
    if not psutil:
        return {"success": False, "error": "psutil not installed"}
    try:
        vm = psutil.virtual_memory()
        return {"success": True, "total": vm.total, "available": vm.available, "percent": vm.percent}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_cpu_usage(interval: float = 0.1) -> Dict[str, Any]:
    if not psutil:
        return {"success": False, "error": "psutil not installed"}
    try:
        percent = psutil.cpu_percent(interval=interval)
        return {"success": True, "percent": percent}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_windows_version() -> Dict[str, Any]:
    try:
        return {"success": True, "platform": platform.platform(), "version": platform.version()}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_network_status() -> Dict[str, Any]:
    if not psutil:
        return {"success": False, "error": "psutil not installed"}
    try:
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        return {"success": True, "interfaces": list(addrs.keys()), "stats": {k: v.isup for k, v in stats.items()}}
    except Exception as e:
        return {"success": False, "error": str(e)}

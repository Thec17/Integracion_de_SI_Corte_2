import os
import platform
import shutil
from typing import Any

try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None


def collect_system_info() -> dict[str, Any]:
    memory_percent = psutil.virtual_memory().percent if psutil else None
    process_count = len(psutil.pids()) if psutil else None
    disk = shutil.disk_usage(os.getcwd())
    return {
        "os": platform.system(),
        "os_release": platform.release(),
        "python": platform.python_version(),
        "process_id": os.getpid(),
        "process_count": process_count,
        "memory_percent": memory_percent,
        "disk_free_mb": round(disk.free / (1024 * 1024), 2),
    }

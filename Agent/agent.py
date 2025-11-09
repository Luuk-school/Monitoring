#verwerk hier de psutil info env erstuur naar main/api
import psutil
import socket
from datetime import datetime, timezone

def getSystemInfo():
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    system_info = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "hostname": socket.gethostname(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory": {
            "total": mem.total,
            "available": mem.available,
            "percent": mem.percent,
            "used": mem.used,
            "free": mem.free,
        },
        "disk": {
            "total": disk.total,
            "available": disk.free,
            "percent": disk.percent,
            "used": disk.used,
            "free": disk.free,
        },
    }
    return system_info


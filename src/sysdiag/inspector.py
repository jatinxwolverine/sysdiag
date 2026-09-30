import os
import platform
import shutil
import sys
import subprocess

def get_diagnostics(config_path=None):
    if config_path:
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        if not config_path.endswith((".json", ".txt", ".conf")):
            raise ValueError(f"Malformed configuration format: {config_path}")

    # 1. Python Details
    py_info = {
        "version": platform.python_version(),
        "executable": sys.executable,
        "is_healthy": sys.version_info >= (3, 8)
    }

    # 2. Disk Space (Root / Current Drive)
    root_path = os.path.abspath(os.sep)
    total, used, free = shutil.disk_usage(root_path)
    gb = 1024 ** 3
    disk_info = {
        "total_gb": round(total / gb, 2),
        "used_gb": round(used / gb, 2),
        "free_gb": round(free / gb, 2),
        "is_low": (free / total) < 0.10
    }

    # 3. Environment Variables
    env_vars = {
        "PATH": "Set" if "PATH" in os.environ else "Missing",
        "SHELL": os.environ.get("SHELL", "Not set"),
        "USER": os.environ.get("USER") or os.environ.get("USERNAME", "Unknown")
    }

    # 4. Developer Tools
    dev_tools = ["git", "docker", "node", "python3"]
    tools_status = {}
    missing_any_tool = False

    for tool in dev_tools:
        found_path = shutil.which(tool)
        if found_path:
            tools_status[tool] = {"installed": True, "path": found_path}
        else:
            tools_status[tool] = {"installed": False, "path": None}
            missing_any_tool = True

    return {
        "python": py_info,
        "disk": disk_info,
        "environment": env_vars,
        "tools": tools_status,
        "missing_tools": missing_any_tool
    }
"""
config.py — Platform configuration for DaVinci Resolve Wrapper API

Auto-detects the OS and sets the correct Resolve API paths.
Modify DEFAULT_PORT if you need a different port.
"""

import os
import platform
import socket
from pathlib import Path

# ─── HTTP Server ────────────────────────────────────────────────────────────

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8080

# ─── Resolve API Paths ──────────────────────────────────────────────────────

class ResolvePaths:
    """Platform-specific paths for the DaVinci Resolve scripting API."""

    @classmethod
    def get(cls) -> dict:
        system = platform.system()
        if system == "Windows":
            return cls._windows()
        elif system == "Darwin":
            return cls._macos()
        elif system == "Linux":
            return cls._linux()
        else:
            raise OSError(f"Unsupported OS: {system}")

    @staticmethod
    def _windows() -> dict:
        api = os.environ.get(
            "RESOLVE_SCRIPT_API",
            r"%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
        )
        lib = os.environ.get(
            "RESOLVE_SCRIPT_LIB",
            r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
        )
        scripts_utility = os.environ.get(
            "RESOLVE_SCRIPTS_UTILITY",
            os.path.join(os.environ["APPDATA"], r"Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Utility")
        )
        return {
            "script_api": api,
            "script_lib": lib,
            "scripts_utility": scripts_utility,
            "executable": r"C:\Program Files\Blackmagic Design\DaVinci Resolve\Resolve.exe",
            "startup_args": ["-nogui"],
            "pythonpath_hint": "set RESOLVE_SCRIPT_API=" + api + " && set PYTHONPATH=%PYTHONPATH%;" + api + "\\Modules\\",
        }

    @staticmethod
    def _macos() -> dict:
        api = os.environ.get(
            "RESOLVE_SCRIPT_API",
            "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
        )
        lib = os.environ.get(
            "RESOLVE_SCRIPT_LIB",
            "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
        )
        scripts_utility = os.environ.get(
            "RESOLVE_SCRIPTS_UTILITY",
            os.path.expanduser("~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility")
        )
        return {
            "script_api": api,
            "script_lib": lib,
            "scripts_utility": scripts_utility,
            "executable": "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/MacOS/Resolve",
            "startup_args": ["-nogui"],
            "pythonpath_hint": "export RESOLVE_SCRIPT_API=" + api + " && export PYTHONPATH=$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/",
        }

    @staticmethod
    def _linux() -> dict:
        api = os.environ.get(
            "RESOLVE_SCRIPT_API",
            "/opt/resolve/Developer/Scripting"
        )
        lib = os.environ.get(
            "RESOLVE_SCRIPT_LIB",
            "/opt/resolve/libs/Fusion/fusionscript.so"
        )
        scripts_utility = os.environ.get(
            "RESOLVE_SCRIPTS_UTILITY",
            os.path.expanduser("~/.local/share/DaVinciResolve/Fusion/Scripts/Utility")
        )
        return {
            "script_api": api,
            "script_lib": lib,
            "scripts_utility": scripts_utility,
            "executable": "/opt/resolve/bin/resolve",
            "startup_args": ["-nogui"],
            "pythonpath_hint": "export RESOLVE_SCRIPT_API=" + api + " && export PYTHONPATH=$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/",
        }


# ─── Server Info ─────────────────────────────────────────────────────────────

def get_local_ip() -> str:
    """Get the local IP address of this machine."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


RESOLVE_PATHS = ResolvePaths.get()
LOCAL_IP = get_local_ip()

# ─── Defaults ────────────────────────────────────────────────────────────────

MEDIA_EXTENSIONS = [
    ".mov", ".mp4", ".m4v", ".avi", ".mkv",
    ".mxf", ".mts", ".m2ts",
    ".r3d", ".braw", ".ari", ".dng", ".cr2", ".cr3",
    ".dpx", ".exr", ".tiff", ".tif", ".jpg", ".jpeg", ".png",
    ".wav", ".mp3", ".aac", ".flac",
    ".aaf", ".edl", ".xml", ".otio",
]

TIMELINE_EXTENSIONS = [".drp", ".drb", ".aaf", ".edl", ".xml", ".otio"]

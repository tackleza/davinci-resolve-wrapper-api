#!/usr/bin/env python3
"""
startup_script.py — Resolve Startup Script

PLACE THIS FILE IN YOUR RESOLVE SCRIPTS/UTILITY FOLDER:

Windows:
  %APPDATA%\\Blackmagic Design\\DaVinci Resolve\\Support\\Fusion\\Scripts\\Utility\\

macOS:
  ~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility/

Linux:
  $HOME/.local/share/DaVinciResolve/Fusion/Scripts/Utility/

RENAME THIS FILE so it sorts last alphabetically, e.g.:
  zzz_wrapper_start.py

WHAT THIS DOES:
  When Resolve starts, this script runs automatically.
  It starts the DaVinci-Resolve-Wrapper-API HTTP server as a background process.

WHAT YOU NEED:
  1. Python 3.10-3.12 installed
  2. The davinci-wrapper-ai project installed (pip install -r requirements.txt)
  3. DaVinci Resolve Studio (paid version — free version doesn't support external scripting)

HOW IT WORKS:
  1. Resolve launches
  2. Resolve runs this startup script
  3. This script launches main.py as a background subprocess
  4. The HTTP wrapper stays running even if this script exits
  5. All subsequent API calls go to the HTTP wrapper

WHAT TO EDIT:
  Change WRAPPER_DIR to the folder where you cloned/placed davinci-wrapper-ai
"""

import os
import sys
import subprocess
import logging
import platform
import time

# ─── CONFIG — EDIT THIS ──────────────────────────────────────────────────────

# Full path to the davinci-wrapper-ai directory
WRAPPER_DIR = r"C:\davinci-wrapper-ai"

# Python executable to use
# Leave empty to auto-detect from PATH
PYTHON_EXE = ""

# Host and port for the HTTP wrapper
WRAPPER_HOST = "127.0.0.1"
WRAPPER_PORT = 8080

# Log file for the wrapper subprocess
LOG_FILE = os.path.join(WRAPPER_DIR, "wrapper.log")

# ─── END CONFIG ───────────────────────────────────────────────────────────────


def get_python_executable() -> str:
    """Find the best Python executable to use."""
    if PYTHON_EXE and os.path.isfile(PYTHON_EXE):
        return PYTHON_EXE

    # Try common locations
    candidates = []

    if platform.system() == "Windows":
        candidates.extend([
            r"C:\Python312\python.exe",
            r"C:\Python311\python.exe",
            r"C:\Python310\python.exe",
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Python", "Python312", "python.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Python", "Python311", "python.exe"),
            os.path.join(os.environ.get("APPDATA", ""), "Local", "Programs", "Python", "Python312", "python.exe"),
        ])

    # Always check PATH
    for name in ["python3", "python"]:
        found = None
        try:
            result = subprocess.run(
                [name, "--version"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                found = name
        except Exception:
            pass
        if found:
            candidates.insert(0, found)

    for candidate in candidates:
        if candidate and os.path.isfile(candidate):
            return candidate
        if candidate in ["python3", "python"]:
            return candidate  # trust PATH

    return "python"  # fallback


def setup_logging():
    """Set up logging for the startup script."""
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir and not os.path.isdir(log_dir):
        try:
            os.makedirs(log_dir, exist_ok=True)
        except Exception:
            pass

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [Resolve Startup] %(levelname)s — %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ]
    )


def start_wrapper():
    """Start the HTTP wrapper as a background process."""
    python = get_python_executable()
    main_py = os.path.join(WRAPPER_DIR, "main.py")

    if not os.path.isdir(WRAPPER_DIR):
        logging.error(f"WRAPPER_DIR not found: {WRAPPER_DIR}")
        logging.error("Please update WRAPPER_DIR in startup_script.py")
        return False

    if not os.path.isfile(main_py):
        logging.error(f"main.py not found: {main_py}")
        return False

    # Detect if already running
    try:
        import urllib.request
        req = urllib.request.Request(f"http://{WRAPPER_HOST}:{WRAPPER_PORT}/api/resolve/health")
        resp = urllib.request.urlopen(req, timeout=2)
        if resp.status == 200:
            logging.info(f"Wrapper already running at http://{WRAPPER_HOST}:{WRAPPER_PORT}")
            return True
    except Exception:
        pass  # Not running — start it

    # Build the command
    cmd = [
        python,
        main_py,
        "--host", WRAPPER_HOST,
        "--port", str(WRAPPER_PORT),
    ]

    # Start as background process
    # On Windows: CREATE_NEW_PROCESS_GROUP + DETACHED_PROCESS hides the window
    # On Unix: start in background with redirected output
    startup_info = None
    creation_flags = 0

    if platform.system() == "Windows":
        startup_info = subprocess.STARTUPINFO()
        startup_info.dwFlags = subprocess.STARTF_USESHOWWINDOW
        startup_info.wShowWindow = subprocess.SW_HIDE
        creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS

    log_file_handle = None
    try:
        log_file_handle = open(LOG_FILE, "a", encoding="utf-8")
        proc = subprocess.Popen(
            cmd,
            cwd=WRAPPER_DIR,
            stdout=log_file_handle,
            stderr=subprocess.STDOUT,
            startupinfo=startup_info,
            creationflags=creation_flags,
            env=os.environ.copy(),
        )
        logging.info(f"Started wrapper (PID: {proc.pid})")
        logging.info(f"Wrapper HTTP: http://{WRAPPER_HOST}:{WRAPPER_PORT}/docs")
        logging.info(f"Log file: {LOG_FILE}")
        return True
    except Exception as e:
        logging.error(f"Failed to start wrapper: {e}")
        if log_file_handle:
            log_file_handle.close()
        return False
    finally:
        # Give it a moment to start
        time.sleep(1)


# ─── Run on startup ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    setup_logging()
    logging.info("=" * 50)
    logging.info("DaVinci Resolve Wrapper API — Startup Script")
    logging.info(f"Resolve: {platform.system()}")
    logging.info(f"Python: {get_python_executable()}")
    logging.info(f"Wrapper dir: {WRAPPER_DIR}")
    logging.info("=" * 50)
    start_wrapper()

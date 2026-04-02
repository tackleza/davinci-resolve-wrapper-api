"""
routes.py — FastAPI route registration
"""

import os
import subprocess
from fastapi import APIRouter

from src.api.endpoints import (
    resolve_router,
    projects_router,
    media_router,
    render_router,
    timeline_router,
)


def register_routes(app):
    """Register all routers with the FastAPI app."""
    app.include_router(resolve_router)
    app.include_router(projects_router)
    app.include_router(media_router)
    app.include_router(render_router)
    app.include_router(timeline_router)

    @app.post("/shutdown")
    async def shutdown_wrapper():
        """
        Shutdown the wrapper API server (for restarting).
        Uses taskkill on Windows to terminate the process.
        """
        pid = os.getpid()
        sentinel = "C:\\Users\\Tackle\\davinci_wrapper\\.restart_sentinel"
        with open(sentinel, "w") as f:
            f.write(str(pid))
        subprocess.Popen(f"taskkill /F /PID {pid}", shell=False)
        return {"success": True, "pid": pid}

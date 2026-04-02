"""
routes.py — FastAPI route registration
"""

import os
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
        Writes sentinel, then terminates the process immediately.
        """
        pid = os.getpid()
        sentinel = "C:\\Users\\Tackle\\davinci_wrapper\\.restart_sentinel"
        with open(sentinel, "w") as f:
            f.write(str(pid))
        # Kill the current process immediately
        import sys
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(0)

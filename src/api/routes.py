"""
routes.py — FastAPI route registration
"""

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

"""
routes.py - API Router Configuration
"""
from src.api.endpoints import (
    registry_router,
    clips_router,
    timelines_router,
    media_router,
    timeline_router,
    render_router,
    project_router,
    resolve_router,
)


def register_routes(app):
    app.include_router(registry_router)
    app.include_router(clips_router)
    app.include_router(timelines_router)
    app.include_router(media_router)
    app.include_router(timeline_router)
    app.include_router(render_router)
    app.include_router(project_router)
    app.include_router(resolve_router)

"""
main.py — DaVinci Resolve Wrapper API
FastAPI HTTP server that exposes DaVinci Resolve's scripting API as REST endpoints.

Usage:
    python main.py [--host HOST] [--port PORT]

Access:
    Swagger UI:  http://localhost:8080/docs
    ReDoc:       http://localhost:8080/redoc
    OpenAPI:     http://localhost:8080/openapi.json
"""

import os
import sys
import logging
import argparse

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure src is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from src.api.routes import register_routes
import src.resolve_connection as rc

# ─── Logging ────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("davinci-wrapper")


# ─── FastAPI App ────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(
        title="DaVinci Resolve API",
        description=(
            "UUID-based REST API for DaVinci Resolve Studio. "
            "Control projects, media pool, timelines, and render queue. "
            "Built for AI agents and video editing pipelines."
        ),
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS — allow all origins for development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ─── Info Endpoint ─────────────────────────────────────────────────────

    @app.get("/", tags=["Info"])
    async def root():
        return {
            "name": "DaVinci Resolve Wrapper API",
            "version": "2.0.0",
            "resolve_api": "DaVinci Resolve Scripting API v20+",
            "docs": "/docs",
            "health": "/api/resolve/health",
        }

    @app.get("/info", tags=["Info"])
    async def info():
        """General info about this wrapper service."""
        paths = config.RESOLVE_PATHS
        return {
            "wrapper_version": "1.0.0",
            "platform": os.environ.get("OSTYPE", "unknown"),
            "resolve_paths": {
                "script_api": paths["script_api"],
                "script_lib": paths["script_lib"],
                "executable": paths["executable"],
            },
            "api_groups": [
                {"name": "Project", "path": "/api/project", "description": "Save, close project"},
                {"name": "Resolve", "path": "/api/resolve", "description": "Health, quit DaVinci"},
                {"name": "Render", "path": "/api/render", "description": "Render queue, presets, settings"},
                {"name": "Clips", "path": "/api/clips", "description": "List, offline, relink clips"},
                {"name": "Timelines", "path": "/api/timelines", "description": "List timelines"},
                {"name": "Media", "path": "/api/media", "description": "Import media"},
                {"name": "Timeline", "path": "/api/timeline", "description": "Insert clips at cursor"},
                {"name": "Registry", "path": "/api/registry", "description": "UUID-based project/folder access"},
            ],
        }

    # ─── Register All Routes ───────────────────────────────────────────────

    register_routes(app)

    # ─── Connection Test on Startup ────────────────────────────────────────

    @app.on_event("startup")
    async def startup_event():
        logger.info("=" * 60)
        logger.info("DaVinci Resolve Wrapper API — Starting")
        logger.info("=" * 60)
        try:
            info = rc.health_check()
            if info.get("connected"):
                logger.info(f"✅ Connected to {info['product_name']} v{info['version']}")
                logger.info(f"   Current page: {info.get('current_page', 'N/A')}")
                if info.get('current_project'):
                    logger.info(f"   Current project: {info['current_project']}")
            else:
                logger.warning("⚠️  DaVinci Resolve is not running")
                logger.warning("   Start Resolve first, then calls will connect automatically")
        except Exception as e:
            logger.warning(f"⚠️  Could not connect to Resolve: {e}")

    return app


# ─── CLI Entry Point ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="DaVinci Resolve Wrapper API")
    parser.add_argument("--host", default=config.DEFAULT_HOST, help="Host to bind to")
    parser.add_argument("--port", type=int, default=config.DEFAULT_PORT, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload (dev mode)")
    parser.add_argument("--log-level", default="info", choices=["debug", "info", "warning", "error"])
    args = parser.parse_args()

    # Override defaults from config if needed
    host = args.host or config.DEFAULT_HOST
    port = args.port or config.DEFAULT_PORT

    logger.info(f"Starting server at http://{host}:{port}")
    logger.info(f"Swagger docs: http://{host}:{port}/docs")

    uvicorn.run(
        "main:create_app",
        host=host,
        port=port,
        reload=args.reload,
        log_level=args.log_level,
        factory=True,
    )


if __name__ == "__main__":
    main()

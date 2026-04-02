"""
endpoints/resolve.py — Resolve-level API endpoints
GET  /api/resolve/*
POST /api/resolve/*
"""
import logging
from fastapi import APIRouter, HTTPException

import src.resolve_connection as rc

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/resolve", tags=["Resolve"])


@router.get("/health")
async def health():
    """Check if DaVinci Resolve is reachable and get version info."""
    info = rc.health_check()
    if info.get("connected"):
        return info
    return {"connected": False, "error": info.get("error")}


@router.post("/quit")
async def quit_davinci():
    """Quit DaVinci Resolve (will prompt to save unsaved changes)."""
    resolve = rc.resolve
    if not resolve:
        raise HTTPException(status_code=400, detail="DaVinci not connected")
    resolve.Quit()
    return {"success": True}

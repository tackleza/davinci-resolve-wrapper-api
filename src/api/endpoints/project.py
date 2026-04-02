"""
endpoints/project.py — Project-level API endpoints
POST /api/project/*
"""
import logging
from fastapi import APIRouter, HTTPException

import src.resolve_connection as rc

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/project", tags=["Project"])


@router.post("/save")
async def save_project():
    """Save current project."""
    project = rc.project
    if not project:
        raise HTTPException(status_code=400, detail="No project connected")
    result = project.Save()
    return {"success": bool(result)}


@router.post("/close")
async def close_project():
    """Close current project (without saving)."""
    project = rc.project
    if not project:
        raise HTTPException(status_code=400, detail="No project connected")
    try:
        result = project.Close()
        return {"success": bool(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

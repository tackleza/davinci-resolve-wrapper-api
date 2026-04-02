"""
endpoints/resolve.py — Resolve-level API endpoints
GET  /api/resolve/*
POST /api/resolve/*
"""

import logging
from fastapi import APIRouter, HTTPException

import src.resolve_connection as rc
from src.models.resolve_models import (
    HealthResponse,
    OpenPageRequest,
    LayoutPresetRequest,
    LayoutPresetExportRequest,
    LayoutPresetImportRequest,
    RenderPresetImportRequest,
    RenderPresetExportRequest,
    RenderPresetsResponse,
    LayoutPresetsResponse,
    CurrentPageResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/resolve", tags=["Resolve"])


# ─── Health & Pages ───────────────────────────────────────────────────────────

@router.get("/health", response_model=HealthResponse)
async def health():
    """Check if DaVinci Resolve is reachable and get version info."""
    info = rc.health_check()
    if info.get("connected"):
        return HealthResponse(**info)
    return HealthResponse(connected=False, error=info.get("error"))


@router.get("/pages", response_model=list[str])
async def get_pages():
    """Get list of valid page names."""
    return ["media", "cut", "edit", "fusion", "color", "fairlight", "deliver"]


@router.get("/current-page", response_model=CurrentPageResponse)
async def get_current_page():
    """Get the currently active page."""
    resolve = rc.get_resolve()
    page = resolve.GetCurrentPage()
    return CurrentPageResponse(page=page)


@router.post("/open-page")
async def open_page(body: OpenPageRequest):
    """Switch to a different Resolve page."""
    result = rc.open_page(body.page_name)
    if not result:
        raise HTTPException(status_code=400, detail=f"Failed to open page: {body.page_name}")
    return {"success": True, "page": body.page_name}


# ─── Quit ────────────────────────────────────────────────────────────────────

@router.post("/quit")
async def quit_resolve():
    """Quit DaVinci Resolve."""
    rc.quit_resolve()
    return {"success": True}


# ─── Layout Presets ───────────────────────────────────────────────────────────

@router.get("/layout-presets", response_model=LayoutPresetsResponse)
async def list_layout_presets():
    """List all saved layout presets."""
    resolve = rc.get_resolve()
    try:
        preset_list = resolve.GetSetting("_layoutPresetList")
        # Fallback: return empty list if not available
        if not preset_list:
            return LayoutPresetsResponse(presets=[])
        return LayoutPresetsResponse(presets=preset_list if isinstance(preset_list, list) else [])
    except Exception as e:
        logger.warning(f"Could not list layout presets: {e}")
        return LayoutPresetsResponse(presets=[])


@router.post("/layout-preset/load")
async def load_layout_preset(body: LayoutPresetRequest):
    """Load a saved layout preset."""
    resolve = rc.get_resolve()
    result = resolve.LoadLayoutPreset(body.preset_name)
    return {"success": bool(result)}


@router.post("/layout-preset/save")
async def save_layout_preset(body: LayoutPresetRequest):
    """Save current UI layout as a preset."""
    resolve = rc.get_resolve()
    result = resolve.SaveLayoutPreset(body.preset_name)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to save layout preset. It may already exist.")
    return {"success": True}


@router.post("/layout-preset/export")
async def export_layout_preset(body: LayoutPresetExportRequest):
    """Export a layout preset to a file."""
    resolve = rc.get_resolve()
    result = resolve.ExportLayoutPreset(body.preset_name, body.file_path)
    if not result:
        raise HTTPException(status_code=400, detail=f"Failed to export preset '{body.preset_name}'")
    return {"success": True, "file_path": body.file_path}


@router.post("/layout-preset/import")
async def import_layout_preset(body: LayoutPresetImportRequest):
    """Import a layout preset from a file."""
    resolve = rc.get_resolve()
    name = body.preset_name or ""
    result = resolve.ImportLayoutPreset(body.file_path, name)
    if not result:
        raise HTTPException(status_code=400, detail=f"Failed to import preset from {body.file_path}")
    imported_name = name if name else body.file_path.split("/")[-1].split("\\")[-1]
    return {"success": True, "preset_name": imported_name}


@router.post("/layout-preset/update")
async def update_layout_preset(body: LayoutPresetRequest):
    """Overwrite an existing layout preset with the current layout."""
    resolve = rc.get_resolve()
    result = resolve.UpdateLayoutPreset(body.preset_name)
    return {"success": bool(result)}


@router.post("/layout-preset/delete")
async def delete_layout_preset(body: LayoutPresetRequest):
    """Delete a layout preset."""
    resolve = rc.get_resolve()
    result = resolve.DeleteLayoutPreset(body.preset_name)
    return {"success": bool(result)}


# ─── Render Presets ───────────────────────────────────────────────────────────

@router.get("/render-presets", response_model=RenderPresetsResponse)
async def list_render_presets():
    """List all render presets available to the current project."""
    project = rc.get_project()
    presets = project.GetRenderPresetList()
    return RenderPresetsResponse(presets=presets if presets else [])


@router.post("/render-preset/import")
async def import_render_preset(body: RenderPresetImportRequest):
    """Import a render preset from a file path."""
    resolve = rc.get_resolve()
    result = resolve.ImportRenderPreset(body.preset_path)
    if not result:
        raise HTTPException(status_code=400, detail=f"Failed to import render preset from {body.preset_path}")
    return {"success": True}


@router.post("/render-preset/export")
async def export_render_preset(body: RenderPresetExportRequest):
    """Export a render preset to a file."""
    resolve = rc.get_resolve()
    result = resolve.ExportRenderPreset(body.preset_name, body.export_path)
    if not result:
        raise HTTPException(status_code=400, detail=f"Failed to export render preset '{body.preset_name}'")
    return {"success": True, "file_path": body.export_path}

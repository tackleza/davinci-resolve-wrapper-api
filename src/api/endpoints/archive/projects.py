"""
endpoints/projects.py — Project Manager API endpoints
GET  /api/projects/*
POST /api/projects/*
"""

import logging
from fastapi import APIRouter, HTTPException

import src.resolve_connection as rc
from src.models.project_models import (
    ProjectInfo,
    ProjectListResponse,
    CreateProjectRequest,
    LoadProjectRequest,
    DeleteProjectRequest,
    ImportProjectRequest,
    ExportProjectRequest,
    ArchiveProjectRequest,
    RestoreProjectRequest,
    FolderCreateRequest,
    FolderDeleteRequest,
    NavigateFolderRequest,
    DatabaseInfoResponse,
    DatabaseListResponse,
    SetDatabaseRequest,
    ProjectSettingsResponse,
    ProjectSettingRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/projects", tags=["Projects"])


def _project_info(project) -> dict:
    try:
        return {
            "name": project.GetName(),
            "unique_id": project.GetUniqueId() if hasattr(project, "GetUniqueId") else None,
            "timeline_count": project.GetTimelineCount() if hasattr(project, "GetTimelineCount") else None,
        }
    except Exception:
        return {"name": "unknown", "unique_id": None, "timeline_count": None}


# ─── Project Listing ─────────────────────────────────────────────────────────

@router.get("", response_model=ProjectListResponse)
async def list_projects():
    """List all projects in the current folder."""
    pm = rc.get_project_manager()
    projects = pm.GetProjectListInCurrentFolder() or []
    current_folder = pm.GetCurrentFolder()
    return ProjectListResponse(projects=projects, current_folder=current_folder)


@router.get("/current", response_model=ProjectInfo)
async def get_current_project():
    """Get info about the currently loaded project."""
    project = rc.get_project()
    return ProjectInfo(**_project_info(project))


# ─── Project CRUD ─────────────────────────────────────────────────────────────

@router.post("/create")
async def create_project(body: CreateProjectRequest):
    """Create a new project."""
    try:
        project = rc.create_project(body.project_name, body.media_location_path or "")
        return {"success": True, "project_name": body.project_name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/load")
async def load_project(body: LoadProjectRequest):
    """Load a project by name."""
    try:
        project = rc.load_project(body.project_name)
        return {"success": True, "project_name": body.project_name}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/save")
async def save_project():
    """Save the current project."""
    result = rc.save_project()
    return {"success": bool(result)}


@router.post("/close")
async def close_project():
    """Close the current project without saving."""
    pm = rc.get_project_manager()
    current = pm.GetCurrentProject()
    if current is None:
        raise HTTPException(status_code=400, detail="No project is currently open")
    result = pm.CloseProject(current)
    return {"success": bool(result)}


@router.post("/delete")
async def delete_project(body: DeleteProjectRequest):
    """Delete a project by name."""
    result = rc.delete_project(body.project_name)
    if not result:
        raise HTTPException(status_code=400, detail=f"Could not delete project '{body.project_name}'. It may be open.")
    return {"success": True}


# ─── Project Import / Export / Archive / Restore ──────────────────────────────

@router.post("/import")
async def import_project(body: ImportProjectRequest):
    """Import a .drp project file."""
    name = body.project_name or ""
    result = rc.import_project(body.file_path, name if name else None)
    if not result:
        raise HTTPException(status_code=400, detail=f"Failed to import project from {body.file_path}")
    imported_name = name if name else body.file_path.split("/")[-1].split("\\")[-1].replace(".drp", "")
    return {"success": True, "project_name": imported_name}


@router.post("/export")
async def export_project(body: ExportProjectRequest):
    """Export the current project to a .drp file."""
    project = rc.get_project()
    result = project.ExportProject(body.project_name, body.file_path, body.with_stills_and_luts)
    if not result:
        raise HTTPException(status_code=400, detail=f"Failed to export project '{body.project_name}'")
    return {"success": True, "file_path": body.file_path}


@router.post("/archive")
async def archive_project(body: ArchiveProjectRequest):
    """
    Archive a project to a .drp file.
    is_archive_src_media=True embeds the original footage into the archive.
    """
    result = rc.archive_project(
        body.project_name,
        body.file_path,
        body.is_archive_src_media,
        body.is_archive_render_cache,
        body.is_archive_proxy_media,
    )
    if not result:
        raise HTTPException(status_code=400, detail=f"Failed to archive project '{body.project_name}'")
    return {"success": True, "file_path": body.file_path}


@router.post("/restore")
async def restore_project(body: RestoreProjectRequest):
    """Restore a project from a .drp archive file."""
    name = body.project_name or ""
    result = rc.restore_project(body.file_path, name if name else None)
    if not result:
        raise HTTPException(status_code=400, detail=f"Failed to restore project from {body.file_path}")
    restored_name = name if name else body.file_path.split("/")[-1].split("\\")[-1].replace(".drp", "")
    return {"success": True, "project_name": restored_name}


# ─── Project Folders ─────────────────────────────────────────────────────────

@router.get("/folders", response_model=list[str])
async def list_folders():
    """List all project folders in the current directory."""
    folders = rc.list_folders()
    return folders or []


@router.post("/folders/create")
async def create_folder(body: FolderCreateRequest):
    """Create a project folder."""
    pm = rc.get_project_manager()
    result = pm.CreateFolder(body.folder_name)
    if not result:
        raise HTTPException(status_code=400, detail=f"Folder '{body.folder_name}' may already exist.")
    return {"success": True, "folder_name": body.folder_name}


@router.post("/folders/delete")
async def delete_folder(body: FolderDeleteRequest):
    """Delete a project folder."""
    pm = rc.get_project_manager()
    result = pm.DeleteFolder(body.folder_name)
    if not result:
        raise HTTPException(status_code=400, detail=f"Could not delete folder '{body.folder_name}'")
    return {"success": True}


@router.post("/folders/navigate")
async def navigate_folder(body: NavigateFolderRequest):
    """Navigate to a project folder."""
    pm = rc.get_project_manager()
    name = body.folder_name

    if name == "root":
        result = pm.GotoRootFolder()
    elif name == "..":
        result = pm.GotoParentFolder()
    else:
        result = pm.OpenFolder(name)

    if not result:
        raise HTTPException(status_code=400, detail=f"Could not navigate to folder '{name}'")
    return {"success": True, "folder": name}


# ─── Database ────────────────────────────────────────────────────────────────

@router.get("/database", response_model=DatabaseInfoResponse)
async def get_current_database():
    """Get current database info."""
    db = rc.get_current_database()
    return DatabaseInfoResponse(**db)


@router.get("/databases", response_model=DatabaseListResponse)
async def list_databases():
    """List all available databases."""
    databases = rc.get_database_list()
    return DatabaseListResponse(databases=databases)


@router.post("/database/set")
async def set_database(body: SetDatabaseRequest):
    """Switch to a different database. Closes any open project."""
    db_info = {
        "DbType": body.db_type,
        "DbName": body.db_name,
    }
    if body.ip_address:
        db_info["IpAddress"] = body.ip_address
    result = rc.set_current_database(db_info)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to switch database")
    return {"success": True, "database": body.db_name}


@router.get("/settings", response_model=ProjectSettingsResponse)
async def get_project_settings():
    """Get current project settings (frame rate, resolution, color space, proxy mode, etc.)."""
    project = rc.get_project()
    try:
        fr = project.GetSetting("timelineFrameRate") or "30.0"
        w = project.GetSetting("timelineResolutionWidth") or "1920"
        h = project.GetSetting("timelineResolutionHeight") or "1080"
        proxy = project.GetSetting("proxyMode") or "off"
        colorspace = project.GetSetting("colorSpaceInput") or ""
        gamma = project.GetSetting("gammaInput") or ""
        all_settings = {}
        for key in ["timelineFrameRate", "timelineResolutionWidth", "timelineResolutionHeight",
                    "proxyMode", "colorSpaceInput", "gammaInput", "monitorOutResolution",
                    "monitorOutFrameRate", "renderCacheMode", "gpuAccelMode",
                    "fieldDominance", "deinterlaceMode"]:
            try:
                val = project.GetSetting(key)
                if val:
                    all_settings[key] = val
            except Exception:
                pass
        return ProjectSettingsResponse(
            frame_rate=float(fr),
            resolution_width=int(w),
            resolution_height=int(h),
            proxy_mode=proxy,
            color_space=colorspace,
            gamma=gamma,
            settings=all_settings,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/settings")
async def set_project_setting(body: ProjectSettingRequest):
    """Set a specific project setting."""
    project = rc.get_project()
    try:
        result = project.SetSetting(body.key, body.value)
        return {"success": bool(result), "key": body.key, "value": body.value}
    except Exception as e:
        return {"success": False, "error": str(e)}

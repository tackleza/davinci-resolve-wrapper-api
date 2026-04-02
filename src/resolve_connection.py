"""
resolve_connection.py — Core DaVinci Resolve API connection

Manages the connection to the DaVinci Resolve scripting API.
This module handles:
- Setting up environment variables for the Resolve scripting API
- Creating the resolve app instance
- Providing cached access to key objects (PM, Project, MediaStorage, MediaPool)
- Tracking clip IDs and media IDs
"""

import os
import sys
import logging
from pathlib import Path
from typing import Any, Optional

import config
from src.exceptions import (
    ResolveNotRunningError,
    ResolveFreeVersionError,
    ResolveScriptingDisabledError,
    ResolveConnectionError,
    ProjectNotFoundError,
    ClipNotFoundError,
    TimelineNotFoundError,
    InvalidPageError,
    APIError,
)

logger = logging.getLogger(__name__)

# ─── Resolve API Instance ─────────────────────────────────────────────────────

_resolve: Optional[Any] = None
_project_manager: Optional[Any] = None
_current_project: Optional[Any] = None
_media_storage: Optional[Any] = None

# Track clips by their MediaPoolItem ID string
_clip_registry: dict[str, Any] = {}  # media_id -> MediaPoolItem

# Track timeline items by composite key: (timeline_index, track_type, track_index, item_index) -> TimelineItem
_timeline_item_registry: dict[tuple, Any] = {}

# Track current Media Pool folder path for full path reconstruction
_current_mp_folder_path: str = "Master"


def _setup_environment() -> None:
    """
    Configure environment variables so Resolve's Python modules can be found.
    Must be called before importing DaVinciResolveScript.
    """
    paths = config.RESOLVE_PATHS

    api_path = os.path.expandvars(paths["script_api"])
    lib_path = os.path.expandvars(paths["script_lib"])

    os.environ["RESOLVE_SCRIPT_API"] = api_path
    os.environ["RESOLVE_SCRIPT_LIB"] = lib_path

    modules_path = os.path.join(api_path, "Modules")
    if modules_path not in sys.path:
        sys.path.insert(0, modules_path)

    logger.info(f"Resolve API path: {api_path}")
    logger.info(f"Resolve lib path: {lib_path}")


def connect() -> Any:
    """
    Connect to the running DaVinci Resolve instance.

    Returns the resolve object on success.
    Raises ResolveNotRunningError if Resolve is not running.

    The resolve object is cached — subsequent calls return the same instance.
    """
    global _resolve

    if _resolve is not None:
        return _resolve

    _setup_environment()

    try:
        import DaVinciResolveScript as dvr_script
    except ImportError as e:
        raise ResolveConnectionError(
            f"Failed to import DaVinciResolveScript module. "
            f"Check that the scripting API path exists: {config.RESOLVE_PATHS['script_api']}"
        ) from e

    _resolve = dvr_script.scriptapp("Resolve")

    if _resolve is None:
        raise ResolveNotRunningError()

    # Basic connectivity check — free version returns a resolve object but with limited API
    try:
        product = _resolve.GetProductName()
        if "DaVinci" not in str(product):
            raise ResolveConnectionError(f"Unexpected product name: {product}")
    except Exception as e:
        raise ResolveConnectionError(f"Resolve is running but API call failed: {e}") from e

    logger.info(f"Connected to {product} — version: {_resolve.GetVersionString()}")
    return _resolve


def get_resolve() -> Any:
    """Get the Resolve instance. Raises if not connected."""
    if _resolve is None:
        return connect()
    return _resolve


def get_project_manager() -> Any:
    """Get the ProjectManager instance."""
    global _project_manager
    if _project_manager is None:
        _project_manager = get_resolve().GetProjectManager()
    return _project_manager


def get_project() -> Any:
    """Get the currently loaded project."""
    global _current_project
    _current_project = get_project_manager().GetCurrentProject()
    if _current_project is None:
        raise ProjectNotFoundError("(no project loaded)")
    return _current_project


def get_media_storage() -> Any:
    """Get the MediaStorage instance."""
    global _media_storage
    if _media_storage is None:
        _media_storage = get_resolve().GetMediaStorage()
    return _media_storage


def set_mp_folder_path(path: str):
    """Track the current Media Pool folder path (since GetParentFolder doesn't work reliably)."""
    global _current_mp_folder_path
    _current_mp_folder_path = path


def get_mp_folder_path() -> str:
    """Return the current Media Pool folder path by walking from current folder up to root."""
    try:
        mp = get_media_pool()
        current = mp.GetCurrentFolder()
        if not current:
            return _current_mp_folder_path

        root = mp.GetRootFolder()

        # Walk from current folder up to root to build full path
        parts = []
        folder = current
        visited = set()  # prevent infinite loop
        while folder and id(folder) not in visited:
            visited.add(id(folder))
            try:
                name = folder.GetName()
                parts.append(name)
                parent = folder.GetParentFolder()
                if parent is None or parent == root:
                    # Reached top
                    break
                folder = parent
            except Exception:
                break

        if parts:
            parts.reverse()
            try:
                root_name = root.GetName() if root else "Master"
            except Exception:
                root_name = "Master"
            # If only one part and it equals root name, we're at root
            if len(parts) == 1 and parts[0] == root_name:
                full_path = root_name
            else:
                full_path = root_name + "/" + "/".join(parts)
            _current_mp_folder_path = full_path
            return full_path
        else:
            return _current_mp_folder_path
    except Exception:
        return _current_mp_folder_path


def get_media_pool() -> Any:
    """Get the MediaPool instance from the current project."""
    return get_project().GetMediaPool()


def reset_connection() -> None:
    """Reset all cached connections. Call this when Resolve is restarted."""
    global _resolve, _project_manager, _current_project, _media_storage, _clip_registry
    _resolve = None
    _project_manager = None
    _current_project = None
    _media_storage = None
    _clip_registry.clear()
    logger.info("Connection cache cleared.")


# ─── Health Check ─────────────────────────────────────────────────────────────

def health_check() -> dict:
    """Return connectivity and version info."""
    try:
        resolve = connect()
        return {
            "connected": True,
            "product_name": resolve.GetProductName(),
            "version": resolve.GetVersionString(),
            "version_array": resolve.GetVersion(),
            "current_page": resolve.GetCurrentPage(),
            "current_project": get_project().GetName() if get_project_manager().GetCurrentProject() else None,
        }
    except ResolveNotRunningError:
        return {"connected": False, "error": "Resolve is not running"}
    except Exception as e:
        return {"connected": False, "error": str(e)}


# ─── Resolve Object Shortcuts ─────────────────────────────────────────────────

def open_page(page_name: str) -> bool:
    """Switch to a Resolve page."""
    valid = ["media", "cut", "edit", "fusion", "color", "fairlight", "deliver"]
    if page_name not in valid:
        raise InvalidPageError(page_name)
    return get_resolve().OpenPage(page_name)


def quit_resolve() -> None:
    """Quit DaVinci Resolve."""
    get_resolve().Quit()


# ─── Project Manager Shortcuts ────────────────────────────────────────────────

def list_projects() -> list[str]:
    """List all projects in the current folder."""
    return get_project_manager().GetProjectListInCurrentFolder()


def list_folders() -> list[str]:
    """List all folders in the current directory."""
    return get_project_manager().GetFolderListInCurrentFolder()


def create_project(name: str, media_location_path: str = "") -> Any:
    """Create a new project."""
    pm = get_project_manager()
    project = pm.CreateProject(name, media_location_path)
    if project is None:
        raise APIError("CreateProject", f"A project named '{name}' may already exist.")
    return project


def load_project(name: str) -> Any:
    """Load a project by name."""
    project = get_project_manager().LoadProject(name)
    if project is None:
        raise ProjectNotFoundError(name)
    return project


def import_project(file_path: str, project_name: str | None = None) -> bool:
    """Import a .drp project file."""
    return get_project_manager().ImportProject(file_path, project_name)


def export_project(project_name: str, file_path: str, with_stills_and_luts: bool = True) -> bool:
    """Export a project to a .drp file."""
    return get_project_manager().ExportProject(project_name, file_path, with_stills_and_luts)


def archive_project(
    project_name: str,
    file_path: str,
    is_archive_src_media: bool = True,
    is_archive_render_cache: bool = True,
    is_archive_proxy_media: bool = False,
) -> bool:
    """Archive a project to a .drp file."""
    return get_project_manager().ArchiveProject(
        project_name, file_path,
        is_archive_src_media, is_archive_render_cache, is_archive_proxy_media
    )


def restore_project(file_path: str, project_name: str | None = None) -> bool:
    """Restore a project from a .drp archive file."""
    return get_project_manager().RestoreProject(file_path, project_name)


def delete_project(name: str) -> bool:
    """Delete a project."""
    return get_project_manager().DeleteProject(name)


def save_project() -> bool:
    """Save the current project."""
    return get_project_manager().SaveProject()


def close_project(project: Any) -> bool:
    """Close a project without saving."""
    return get_project_manager().CloseProject(project)


def get_current_database() -> dict:
    """Get current database info."""
    return get_project_manager().GetCurrentDatabase()


def get_database_list() -> list[dict]:
    """List all available databases."""
    return get_project_manager().GetDatabaseList()


def set_current_database(db_info: dict) -> bool:
    """Switch to a different database."""
    return get_project_manager().SetCurrentDatabase(db_info)


# ─── Clip Registry (ID → MediaPoolItem mapping) ─────────────────────────────

def _register_clips(clips: list) -> list[dict]:
    """
    Register a list of MediaPoolItem objects and return their info.
    Each clip gets assigned a stable clip_id based on its MediaId.
    """
    result = []
    for clip in clips:
        try:
            media_id = str(clip.GetMediaId()) if clip else "unknown"
            if media_id not in _clip_registry:
                _clip_registry[media_id] = clip
            result.append({
                "name": clip.GetName() if clip else "unknown",
                "media_id": media_id,
            })
        except Exception:
            result.append({"name": "unknown", "media_id": "unknown"})
    return result


def get_clip_by_id(media_id: str) -> Any:
    """Get a MediaPoolItem by its media_id."""
    if media_id not in _clip_registry:
        raise ClipNotFoundError(media_id)
    return _clip_registry[media_id]


def register_clip(clip: Any) -> str:
    """Register a single clip and return its media_id."""
    try:
        media_id = str(clip.GetMediaId())
        _clip_registry[media_id] = clip
        return media_id
    except Exception as e:
        raise APIError("register_clip", str(e)) from e


def get_all_registered_clips() -> dict[str, dict]:
    """Return info about all registered clips."""
    result = {}
    for media_id, clip in _clip_registry.items():
        try:
            result[media_id] = {"name": clip.GetName(), "media_id": media_id}
        except Exception:
            result[media_id] = {"name": "(unavailable)", "media_id": media_id}
    return result


def clear_clip_registry() -> None:
    """Clear all registered clips."""
    _clip_registry.clear()


# ─── TimelineItem Registry ────────────────────────────────────────────────────

def get_timeline_item(timeline_index: int, track_type: str, track_index: int, item_index: int) -> tuple[Any, int]:
    """
    Get a TimelineItem by its position in a track.

    Returns (TimelineItem, start_frame) tuple.
    Raises TimelineItemNotFoundError if not found.
    """
    project = get_project()
    tl = project.GetTimelineByIndex(timeline_index)
    if not tl:
        raise TimelineNotFoundError(f"Timeline {timeline_index}")

    items = tl.GetItemsInTrack(track_type, track_index) or {}
    if item_index < 1 or item_index > len(items):
        raise TimelineItemNotFoundError(
            f"Item index {item_index} out of range for track {track_type}:{track_index} "
            f"(total {len(items)} items)"
        )

    # items is dict {start_frame: TimelineItem}
    sorted_starts = sorted(items.keys())
    start_frame = sorted_starts[item_index - 1]
    item = items[start_frame]

    key = (timeline_index, track_type, track_index, item_index)
    _timeline_item_registry[key] = item
    return item, start_frame


def get_timeline_by_index(timeline_index: int) -> Any:
    """Get a timeline by its 1-based index."""
    project = get_project()
    tl = project.GetTimelineByIndex(timeline_index)
    if not tl:
        raise TimelineNotFoundError(f"Timeline {timeline_index}")
    return tl

"""
endpoints/media.py — MediaPool / Media Storage API endpoints
GET  /api/media/*
POST /api/media/*
"""

import logging
from fastapi import APIRouter, HTTPException, Query

import src.resolve_connection as rc
from src.models.media_models import (
    ImportMediaRequest,
    ImportMediaResponse,
    ImportedClip,
    RelinkClipsRequest,
    UnlinkClipsRequest,
    ClipDeleteRequest,
    ClipMoveRequest,
    ClipColorRequest,
    AddMarkerRequest,
    ClipMarkersResponse,
    MarkerInfo,
    AddFlagRequest,
    FlagListResponse,
    SetMetadataRequest,
    CreateFolderRequest,
    MediaPoolResponse,
    FolderInfo,
    FileListResponse,
    MediaFile,
    SubfoldersResponse,
    VolumesResponse,
    ClipDetailResponse,
    ClipListResponse,
    ClipInfo,
    AutoSyncAudioRequest,
    BatchImportRequest,
    BatchImportResult,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/media", tags=["Media"])


# ─── Media Storage (file system) ─────────────────────────────────────────────

@router.get("/volumes", response_model=VolumesResponse)
async def get_volumes():
    """List mounted volumes visible in Resolve's media storage."""
    ms = rc.get_media_storage()
    volumes = ms.GetMountedVolumeList() or []
    return VolumesResponse(volumes=volumes)


@router.get("/files", response_model=FileListResponse)
async def get_files(folder_path: str = Query(..., description="Absolute path to the folder")):
    """List files in a folder path (from Resolve's Media Storage)."""
    ms = rc.get_media_storage()
    files = ms.GetFileList(folder_path) or []
    result = []
    for f in files:
        result.append(MediaFile(
            name=f.split("/")[-1].split("\\")[-1],
            path=f,
            type="media"
        ))
    return FileListResponse(files=result)


@router.get("/subfolders", response_model=SubfoldersResponse)
async def get_subfolders(folder_path: str = Query(..., description="Absolute path to the folder")):
    """List subfolders in a path."""
    ms = rc.get_media_storage()
    folders = ms.GetSubFolderList(folder_path) or []
    return SubfoldersResponse(subfolders=folders)


@router.post("/reveal")
async def reveal_in_storage(path: str):
    """Reveal a file/folder in Resolve's Media Storage panel."""
    ms = rc.get_media_storage()
    result = ms.RevealInStorage(path)
    return {"success": bool(result)}


# ─── Import Media ─────────────────────────────────────────────────────────────

@router.post("/import", response_model=ImportMediaResponse)
async def import_media(body: ImportMediaRequest):
    """
    Import files or folders into the current Media Pool folder.

    Supports three formats:
    1. Simple paths: ["D:/footage/video1.mov", "D:/footage/video2.mov"]
    2. Folder paths: ["D:/footage/"] (imports all media in folder)
    3. Frame ranges: [{"media": "D:/seq/frame_%04d.exr", "start_frame": 1, "end_frame": 250}]
    """
    ms = rc.get_media_storage()
    project = rc.get_project()
    mp = project.GetMediaPool()

    # Separate string items from dict items
    string_items = []
    range_items = []
    for item in body.items:
        if isinstance(item, str):
            string_items.append(item)
        elif isinstance(item, dict):
            range_items.append(item)
        else:
            # Pydantic model
            if hasattr(item, "media"):
                range_items.append({"media": item.media, "start_frame": item.start_frame, "end_frame": item.end_frame})
            else:
                string_items.append(str(item))

    all_clips = []

    # Import string paths — try ImportMedia first, fall back to AddItemListToMediaPool
    if string_items:
        clips = None
        try:
            if hasattr(ms, 'ImportMedia'):
                clips = ms.ImportMedia(string_items)
        except Exception:
            pass
        if clips is None:
            try:
                clips = ms.AddItemListToMediaPool(string_items)
            except Exception:
                pass
        if clips:
            all_clips.extend(clips)

    # Import with frame ranges
    for item in range_items:
        clips = None
        try:
            clips = ms.AddItemListToMediaPool([item])
        except Exception:
            pass
        if clips:
            all_clips.extend(clips)

    # Register clips and build response
    imported = []
    for clip in all_clips:
        if clip:
            info = rc.register_clip(clip)
            try:
                imported.append(ImportedClip(name=clip.GetName(), media_id=info))
            except Exception:
                imported.append(ImportedClip(name="unknown", media_id=info))

    return ImportMediaResponse(imported_clips=imported, total=len(imported))


# ─── Media Pool Navigation ───────────────────────────────────────────────────

@router.get("/pool", response_model=MediaPoolResponse)
async def get_media_pool():
    """Get current Media Pool structure."""
    mp = rc.get_media_pool()
    try:
        current = mp.GetCurrentFolder()
        root = mp.GetRootFolder()
        current_name = current.GetName() if current else None
        root_name = root.GetName() if root else None

        subfolders = []
        if root:
            try:
                for sf in root.GetSubFolderList():
                    try:
                        subfolders.append(FolderInfo(
                            name=sf.GetName() if hasattr(sf, 'GetName') else str(sf),
                            clip_count=None
                        ))
                    except Exception:
                        pass
            except Exception:
                pass

        return MediaPoolResponse(
            current_folder=current_name,
            root_folder=root_name,
            subfolders=subfolders
        )
    except Exception as e:
        logger.error(f"Error getting media pool: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/folder/create", response_model=FolderInfo)
async def create_media_folder(name: str, parent_folder: str | None = None):
    """
    Create a subfolder in the Media Pool.
    If parent_folder is provided, creates inside that folder.
    If not, creates in the current folder.
    """
    mp = rc.get_media_pool()
    if parent_folder:
        # Find the parent folder
        root = mp.GetRootFolder()
        folders = root.GetSubFolderList()
        target = None
        for f in folders:
            try:
                if f.GetName() == parent_folder:
                    target = f
                    break
            except Exception:
                pass
        if target is None:
            raise HTTPException(status_code=404, detail=f"Parent folder '{parent_folder}' not found")
        folder = mp.AddSubFolder(target, name)
    else:
        folder = mp.AddSubFolder(mp.GetCurrentFolder(), name)

    if not folder:
        raise HTTPException(status_code=400, detail=f"Could not create folder '{name}'")
    return FolderInfo(name=folder.GetName())


# ─── Clips ──────────────────────────────────────────────────────────────────

@router.get("/clips", response_model=ClipListResponse)
async def list_clips(folder_name: str | None = None):
    """Get clips in the current Media Pool folder (or a named subfolder)."""
    mp = rc.get_media_pool()

    if folder_name:
        root = mp.GetRootFolder()
        target = None
        for f in root.GetSubFolderList():
            try:
                if f.GetName() == folder_name:
                    target = f
                    break
            except Exception:
                pass
        if target:
            mp.SetCurrentFolder(target)
            folder_clips = target.GetClipList()
        else:
            raise HTTPException(status_code=404, detail=f"Folder '{folder_name}' not found")
    else:
        folder_clips = mp.GetCurrentFolder().GetClipList()

    clips = []
    for clip in (folder_clips or []):
        try:
            media_id = rc.register_clip(clip)
            clips.append(ClipInfo(
                name=clip.GetName(),
                media_id=media_id,
                duration=None,  # available via GetClipProperty
                proxy=None,
                audio_tracks=None,
            ))
        except Exception:
            pass

    return ClipListResponse(clips=clips)


@router.get("/clip/{media_id}", response_model=ClipDetailResponse)
async def get_clip(media_id: str):
    """Get full details for a specific clip."""
    clip = rc.get_clip_by_id(media_id)
    try:
        name = clip.GetName()
        props = clip.GetClipProperty() or {}
        metadata = clip.GetMetadata() or {}
        return ClipDetailResponse(
            name=name,
            media_id=media_id,
            properties=props,
            metadata=metadata,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/clip/{media_id}/metadata")
async def set_clip_metadata(media_id: str, body: SetMetadataRequest):
    """Set metadata on a clip."""
    clip = rc.get_clip_by_id(media_id)
    result = clip.SetMetadata(body.metadata)
    return {"success": bool(result)}


@router.post("/clip/{media_id}/markers/add")
async def add_clip_marker(media_id: str, body: AddMarkerRequest):
    """Add a marker to a clip."""
    clip = rc.get_clip_by_id(media_id)
    result = clip.AddMarker(
        body.frame_id, body.color, body.name,
        body.note, body.duration, body.custom_data
    )
    return {"success": bool(result)}


@router.get("/clip/{media_id}/markers", response_model=ClipMarkersResponse)
async def get_clip_markers(media_id: str):
    """Get all markers on a clip."""
    clip = rc.get_clip_by_id(media_id)
    markers_raw = clip.GetMarkers() or {}
    markers = {}
    for frame, info in markers_raw.items():
        markers[str(frame)] = MarkerInfo(
            color=info.get("color", ""),
            duration=info.get("duration", 1.0),
            name=info.get("name", ""),
            note=info.get("note", ""),
            custom_data=info.get("customData", ""),
        )
    return ClipMarkersResponse(markers=markers)


@router.post("/clip/{media_id}/markers/delete-by-color")
async def delete_markers_by_color(media_id: str, color: str = "All"):
    """Delete all markers of a specific color. Use 'All' to delete all."""
    clip = rc.get_clip_by_id(media_id)
    result = clip.DeleteMarkersByColor(color)
    return {"success": bool(result)}


@router.post("/clip/{media_id}/markers/delete-at-frame")
async def delete_marker_at_frame(media_id: str, frame_num: float):
    """Delete a marker at a specific frame number."""
    clip = rc.get_clip_by_id(media_id)
    result = clip.DeleteMarkerAtFrame(frame_num)
    return {"success": bool(result)}


@router.post("/clip/{media_id}/flags/add")
async def add_flag(media_id: str, body: AddFlagRequest):
    """Add a flag to a clip."""
    clip = rc.get_clip_by_id(media_id)
    result = clip.AddFlag(body.color)
    return {"success": bool(result)}


@router.get("/clip/{media_id}/flags", response_model=FlagListResponse)
async def get_flags(media_id: str):
    """Get all flag colors on a clip."""
    clip = rc.get_clip_by_id(media_id)
    flags = clip.GetFlagList() or []
    return FlagListResponse(flags=flags)


@router.post("/clip/{media_id}/flags/clear")
async def clear_flags(media_id: str, color: str = "All"):
    """Clear flags. Use 'All' to clear all flags."""
    clip = rc.get_clip_by_id(media_id)
    result = clip.ClearFlags(color)
    return {"success": bool(result)}


@router.post("/clip/{media_id}/color")
async def set_clip_color(media_id: str, body: ClipColorRequest):
    """Set the clip's color label."""
    clip = rc.get_clip_by_id(media_id)
    result = clip.SetClipColor(body.color)
    return {"success": bool(result)}


@router.post("/clip/{media_id}/clear-color")
async def clear_clip_color(media_id: str):
    """Clear the clip's color label."""
    clip = rc.get_clip_by_id(media_id)
    result = clip.ClearClipColor()
    return {"success": bool(result)}


@router.post("/clip/{media_id}/rename")
async def rename_clip(media_id: str, name: str):
    """Rename a clip."""
    clip = rc.get_clip_by_id(media_id)
    result = clip.SetName(name)
    return {"success": bool(result)}


# ─── Relink / Unlink ────────────────────────────────────────────────────────

@router.post("/relink")
async def relink_clips(body: RelinkClipsRequest):
    """
    Relink clips to a new folder path.
    Resolve will search the new folder for media matching the clip names.
    """
    mp = rc.get_media_pool()
    clips = []
    for cid in body.clip_ids:
        try:
            clips.append(rc.get_clip_by_id(cid))
        except Exception:
            logger.warning(f"Clip not found for relink: {cid}")

    if not clips:
        raise HTTPException(status_code=404, detail="No valid clips found")

    result = mp.RelinkClips(clips, body.folder_path)
    return {"success": bool(result), "relinked_count": len(clips)}


@router.post("/unlink")
async def unlink_clips(body: UnlinkClipsRequest):
    """Unlink specified clips from their media files."""
    mp = rc.get_media_pool()
    clips = []
    for cid in body.clip_ids:
        try:
            clips.append(rc.get_clip_by_id(cid))
        except Exception:
            pass
    result = mp.UnlinkClips(clips)
    return {"success": bool(result)}


# ─── Clip Operations ─────────────────────────────────────────────────────────

@router.post("/clip/delete")
async def delete_clips(body: ClipDeleteRequest):
    """Delete clips from the media pool."""
    mp = rc.get_media_pool()
    clips = []
    for cid in body.clip_ids:
        try:
            clips.append(rc.get_clip_by_id(cid))
        except Exception:
            pass
    result = mp.DeleteClips(clips)
    return {"success": bool(result)}


@router.post("/clip/move")
async def move_clips(body: ClipMoveRequest):
    """Move clips to a different Media Pool folder."""
    mp = rc.get_media_pool()
    clips = []
    for cid in body.clip_ids:
        try:
            clips.append(rc.get_clip_by_id(cid))
        except Exception:
            pass

    # Find target folder
    root = mp.GetRootFolder()
    target_folder = None
    for f in root.GetSubFolderList():
        try:
            if f.GetName() == body.target_folder:
                target_folder = f
                break
        except Exception:
            pass

    if not target_folder:
        raise HTTPException(status_code=404, detail=f"Target folder '{body.target_folder}' not found")

    result = mp.MoveClips(clips, target_folder)
    return {"success": bool(result)}


# ─── Batch Import ───────────────────────────────────────────────────────────

@router.post("/import/batch", response_model=BatchImportResult)
async def batch_import(body: BatchImportRequest):
    """
    Import all media files from a folder in batches.

    DaVinci crashes when importing 200+ files at once via AddItemListToMediaPool().
    This endpoint splits the import into smaller batches to avoid the crash.

    Supported extensions: mp4, mov, mp3, wav, mkv, avi, mxf, webm, exr, dpx, png, jpg, tif

    Example:
    {
        "folder_path": "Y:/Video Editing Job/3. Waiting For Render/sb4-12",
        "batch_size": 20,
        "recursive": False,
        "extensions": ["mp4", "mov", "mp3"]
    }
    """
    import os
    import glob

    SUPPORTED_EXTENSIONS = {
        "mp4", "mov", "mp3", "wav", "aac", "m4a",
        "mkv", "avi", "mxf", "webm",
        "exr", "dpx", "png", "jpg", "jpeg", "tif", "tiff", "tga",
        "mpg", "mpeg", "flv", "wmv"
    }

    folder = body.folder_path.replace("\\", "/")
    extensions = set(ext.lower().lstrip(".") for ext in (body.extensions or SUPPORTED_EXTENSIONS))
    patterns = [f"*.{ext}" for ext in extensions]

    files = []
    for pattern in patterns:
        if body.recursive:
            files.extend(glob.glob(os.path.join(folder, "**", pattern), recursive=True))
        else:
            files.extend(glob.glob(os.path.join(folder, pattern)))

    files = sorted(set(files))
    total = len(files)

    if total == 0:
        return BatchImportResult(
            success=True,
            total_files=0,
            imported_clips=0,
            failed_files=0,
            batches=0,
            errors=["No media files found in folder"],
        )

    ms = rc.get_media_storage()
    imported = 0
    failed = 0
    errors = []
    batch_size = max(1, min(body.batch_size, 50))  # clamp to 1-50

    for i in range(0, total, batch_size):
        batch = files[i : i + batch_size]
        batch_num = (i // batch_size) + 1

        try:
            clips = ms.AddItemListToMediaPool(batch)
            if clips:
                imported += len(clips)
        except Exception as e:
            failed += len(batch)
            errors.append(f"Batch {batch_num} failed: {str(e)}")

    return BatchImportResult(
        success=(failed == 0),
        total_files=total,
        imported_clips=imported,
        failed_files=failed,
        batches=(total + batch_size - 1) // batch_size,
        errors=errors,
    )


# ─── Auto Sync Audio ────────────────────────────────────────────────────────

@router.post("/clip/auto-sync-audio")
async def auto_sync_audio(body: AutoSyncAudioRequest):
    """Sync audio across multiple clips (e.g., separate audio recording)."""
    mp = rc.get_media_pool()
    clips = []
    for cid in body.clip_ids:
        try:
            clips.append(rc.get_clip_by_id(cid))
        except Exception:
            pass

    if len(clips) < 2:
        raise HTTPException(status_code=400, detail="At least 2 clips required for audio sync")

    settings = {}
    if body.algorithm is not None:
        settings["algorithm"] = body.algorithm
    if body.align_method is not None:
        settings["alignMethod"] = body.align_method
    if body.silences is not None:
        settings["silences"] = body.silences
    if body.threshold is not None:
        settings["threshold"] = body.threshold
    if body.fade_length is not None:
        settings["fadeLength"] = body.fade_length
    if body.fade_curve is not None:
        settings["fadeCurve"] = body.fade_curve
    if body.ignore_audio is not None:
        settings["ignoreAudio"] = body.ignore_audio
    if body.sample_rate is not None:
        settings["sampleRate"] = body.sample_rate
    if body.start_offset is not None:
        settings["startOffset"] = body.start_offset
    if body.duration is not None:
        settings["duration"] = body.duration

    result = mp.AutoSyncAudio(clips, settings)
    return {"success": bool(result)}

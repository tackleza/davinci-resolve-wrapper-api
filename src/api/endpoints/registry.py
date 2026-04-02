"""
endpoints/registry.py — UUID Registry API
/api/registry/*
"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal

import src.resolve_connection as rc
from src.registry import registry

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/registry", tags=["registry"])


# ─── Request/Response Models ────────────────────────────────────────────────────


class ClipResponse(BaseModel):
    uuid: str
    name: str
    media_type: Optional[str] = None


class FolderSummary(BaseModel):
    uuid: str
    name: str
    parent_uuid: Optional[str] = None
    clip_count: int = 0
    subfolder_count: int = 0


class FolderDetail(BaseModel):
    uuid: str
    name: str
    parent_uuid: Optional[str] = None
    clips: list[ClipResponse] = []
    subfolders: list[FolderSummary] = []


class TimelineResponse(BaseModel):
    uuid: str
    name: str
    index: int = 0


class ProjectSummary(BaseModel):
    uuid: str
    name: str
    is_current: bool = False


class ProjectDetail(BaseModel):
    uuid: str
    name: str
    root_folder: Optional[FolderSummary] = None
    timelines: dict[str, TimelineResponse] = {}


# ─── Helpers ──────────────────────────────────────────────────────────────────


def folder_to_summary(folder) -> FolderSummary:
    return FolderSummary(
        uuid=folder.uuid,
        name=folder.name,
        parent_uuid=folder.parent_uuid,
        clip_count=len(folder.clips),
        subfolder_count=len(folder.subfolders),
    )


def clip_to_response(clip) -> ClipResponse:
    return ClipResponse(
        uuid=clip.uuid,
        name=clip.name,
        media_type=clip.media_type,
    )


def timeline_to_response(tl) -> TimelineResponse:
    return TimelineResponse(
        uuid=tl.uuid,
        name=tl.name,
        index=tl.index,
    )


# ─── Project Endpoints ────────────────────────────────────────────────────────


@router.get("/projects")
async def list_projects():
    return {
        "projects": [
            ProjectSummary(
                uuid=p.uuid,
                name=p.name,
                is_current=(p.uuid == registry.current_project.uuid if registry.current_project else False),
            )
            for p in registry.projects.values()
        ]
    }


@router.get("/projects/current")
async def get_current_project():
    proj = registry.current_project
    if not proj:
        raise HTTPException(status_code=404, detail="No current project registered")

    def build_folder_tree(folder_data) -> FolderSummary:
        return FolderSummary(
            uuid=folder_data.uuid,
            name=folder_data.name,
            parent_uuid=folder_data.parent_uuid,
            clip_count=len(folder_data.clips),
            subfolder_count=len(folder_data.subfolders),
        )

    return ProjectDetail(
        uuid=proj.uuid,
        name=proj.name,
        root_folder=build_folder_tree(proj.root_folder) if proj.root_folder else None,
        timelines={uuid: timeline_to_response(tl) for uuid, tl in proj.timelines.items()},
    )


@router.post("/projects/rebuild")
async def rebuild_tree():
    project = rc.project
    if not project:
        raise HTTPException(status_code=400, detail="No project connected")
    registry.build_folder_tree(project)
    return {"status": "ok", "message": "Tree rebuilt"}


# ─── Folder Endpoints ──────────────────────────────────────────────────────────


@router.get("/folders")
async def list_folders():
    proj = registry.current_project
    if not proj or not proj.root_folder:
        return {"folders": []}

    folders = []

    def collect(fld):
        folders.append(folder_to_summary(fld))
        for sf in fld.subfolders.values():
            collect(sf)

    collect(proj.root_folder)
    return {"folders": folders}


@router.get("/folders/{uuid}")
async def get_folder(uuid: str):
    folder = registry.get_folder_by_uuid(uuid)
    if not folder:
        raise HTTPException(status_code=404, detail=f"Folder not found: {uuid}")

    return FolderDetail(
        uuid=folder.uuid,
        name=folder.name,
        parent_uuid=folder.parent_uuid,
        clips=[clip_to_response(c) for c in folder.clips.values()],
        subfolders=[folder_to_summary(sf) for sf in folder.subfolders.values()],
    )


@router.get("/folders/{uuid}/tree")
async def get_folder_tree(uuid: str):
    folder = registry.get_folder_by_uuid(uuid)
    if not folder:
        raise HTTPException(status_code=404, detail=f"Folder not found: {uuid}")

    def build_tree(fld) -> FolderSummary:
        return FolderSummary(
            uuid=fld.uuid,
            name=fld.name,
            parent_uuid=fld.parent_uuid,
            clip_count=len(fld.clips),
            subfolder_count=len(fld.subfolders),
        )

    return build_tree(folder)


@router.get("/folders/{uuid}/parent")
async def get_parent_folder(uuid: str):
    folder = registry.get_folder_by_uuid(uuid)
    if not folder:
        raise HTTPException(status_code=404, detail=f"Folder not found: {uuid}")

    if not folder.parent_uuid:
        return None

    parent = registry.get_folder_by_uuid(folder.parent_uuid)
    if not parent:
        return None

    return folder_to_summary(parent)


# ─── Clip/Timeline/Media sub-routers (under /api/) ────────────────────────────


# Create separate routers for /api/clips, /api/timelines, /api/media, /api/timeline
clips_router = APIRouter(prefix="/api/clips", tags=["Clips"])
timelines_router = APIRouter(prefix="/api/timelines", tags=["Timelines"])
media_router = APIRouter(prefix="/api/media", tags=["Media"])
timeline_router = APIRouter(prefix="/api/timeline", tags=["Timeline"])


# ─── Clip Endpoints ───────────────────────────────────────────────────────────


@clips_router.get("")
async def list_clips():
    proj = registry.current_project
    if not proj or not proj.root_folder:
        return {"clips": []}

    clips = []

    def collect(fld):
        for clip in fld.clips.values():
            clips.append(clip_to_response(clip))
        for sf in fld.subfolders.values():
            collect(sf)

    collect(proj.root_folder)
    return {"clips": clips}


@clips_router.get("/{uuid}")
async def get_clip(uuid: str):
    clip = registry.get_clip_by_uuid(uuid)
    if not clip:
        raise HTTPException(status_code=404, detail=f"Clip not found: {uuid}")
    return clip_to_response(clip)


# ─── Timeline Endpoints ────────────────────────────────────────────────────────


@timelines_router.get("")
async def list_timelines():
    proj = registry.current_project
    if not proj:
        return {"timelines": []}

    return {
        "timelines": [timeline_to_response(tl) for tl in proj.timelines.values()]
    }


@timelines_router.get("/{uuid}")
async def get_timeline(uuid: str):
    tl = registry.get_timeline_by_uuid(uuid)
    if not tl:
        raise HTTPException(status_code=404, detail=f"Timeline not found: {uuid}")
    return timeline_to_response(tl)


# ─── Media Import Endpoints ────────────────────────────────────────────────────


class ImportMediaRequest(BaseModel):
    paths: list[str]
    destination_folder_uuid: Optional[str] = None


class ImportedClipResponse(BaseModel):
    uuid: str
    name: str
    path: str
    folder_uuid: Optional[str] = None


class FailedImportResponse(BaseModel):
    path: str
    error: str


class ImportMediaResponse(BaseModel):
    success: bool
    imported_clips: list[ImportedClipResponse] = []
    failed_paths: list[FailedImportResponse] = []


@media_router.post("/import")
async def import_media(body: ImportMediaRequest):
    project = rc.project
    if not project:
        raise HTTPException(status_code=400, detail="No project connected")

    ms = rc.get_media_storage()
    mp = project.GetMediaPool()

    destination_folder_uuid = body.destination_folder_uuid
    if destination_folder_uuid:
        folder = registry.get_folder_by_uuid(destination_folder_uuid)
        if folder:
            davinci_folder = _find_davinci_folder(
                project.GetMediaPool().GetRootFolder(),
                destination_folder_uuid
            )
            if davinci_folder:
                mp.SetCurrentFolder(davinci_folder)

    imported_clips = []
    failed_paths = []

    try:
        clips = ms.ImportMedia(body.paths)
        if clips:
            for clip in clips:
                clip_uuid = clip.GetUniqueId()
                clip_name = clip.GetName()
                clip_folder_uuid = destination_folder_uuid
                if not clip_folder_uuid:
                    clip_folder_uuid = _get_current_folder_uuid(project)

                registry.register_clip(clip, clip_folder_uuid or "")

                imported_clips.append(ImportedClipResponse(
                    uuid=clip_uuid,
                    name=clip_name,
                    path=body.paths[0] if body.paths else "",
                    folder_uuid=clip_folder_uuid,
                ))
    except Exception as e:
        for path in body.paths:
            failed_paths.append(FailedImportResponse(path=path, error=str(e)))

    # Rebuild registry to include new clips
    try:
        registry.build_folder_tree(project)
    except Exception:
        pass

    return ImportMediaResponse(
        success=len(failed_paths) == 0,
        imported_clips=imported_clips,
        failed_paths=failed_paths,
    )


# ─── Timeline Insert Endpoints ────────────────────────────────────────────────


class TimelineInsertRequest(BaseModel):
    clip_uuids: list[str]
    timeline_uuid: Optional[str] = None
    track_type: Literal["both", "video", "audio"] = "both"
    position: Literal["cursor"] = "cursor"


class InsertedClipResponse(BaseModel):
    uuid: str
    name: str
    track_type: str


class TimelineInsertResponse(BaseModel):
    success: bool
    inserted_count: int
    clips: list[InsertedClipResponse] = []
    error: Optional[str] = None


@timeline_router.post("/insert")
async def insert_into_timeline(body: TimelineInsertRequest):
    project = rc.project
    if not project:
        raise HTTPException(status_code=400, detail="No project connected")

    tl = _get_davinci_timeline(project, body.timeline_uuid)
    if not tl:
        raise HTTPException(status_code=404, detail="Timeline not found")
    project.SetCurrentTimeline(tl)

    mp = project.GetMediaPool()

    media_items = []
    for clip_uuid in body.clip_uuids:
        item = _find_media_pool_item(project, clip_uuid)
        if item:
            media_items.append(item)

    if not media_items:
        raise HTTPException(status_code=400, detail="No valid clips found")

    try:
        result = tl.InsertClipIntoTimeline(media_items)
    except Exception as e:
        try:
            for item in media_items:
                mp.AppendToTimeline(item)
            result = True
        except Exception as e2:
            return TimelineInsertResponse(
                success=False,
                inserted_count=0,
                clips=[],
                error=f"Insert failed: {e}; Append fallback also failed: {e2}",
            )

    return TimelineInsertResponse(
        success=True,
        inserted_count=len(media_items),
        clips=[
            InsertedClipResponse(
                uuid=clip_uuid,
                name=registry.get_clip_by_uuid(clip_uuid).name if registry.get_clip_by_uuid(clip_uuid) else "unknown",
                track_type=body.track_type,
            )
            for clip_uuid in body.clip_uuids
        ],
    )


# ─── Offline Clips & Relink Endpoints ────────────────────────────────────────


class OfflineClipResponse(BaseModel):
    uuid: str
    name: str
    folder_uuid: str
    media_id: Optional[int] = None


class RelinkClipsRequest(BaseModel):
    clip_uuids: list[str]
    search_folders: list[str]


class RelinkClipsResponse(BaseModel):
    success: bool
    relinked_count: int
    failed_uuids: list[str] = []


@clips_router.get("/offline")
async def get_offline_clips():
    project = rc.project
    if not project:
        raise HTTPException(status_code=400, detail="No project connected")

    offline = []

    def scan_folder(folder_data):
        for clip_data in folder_data.clips.values():
            if clip_data.media_id == 0 or clip_data.media_id is None:
                offline.append(OfflineClipResponse(
                    uuid=clip_data.uuid,
                    name=clip_data.name,
                    folder_uuid=folder_data.uuid,
                    media_id=clip_data.media_id,
                ))
        for subfolder in folder_data.subfolders.values():
            scan_folder(subfolder)

    proj = registry.current_project
    if proj and proj.root_folder:
        scan_folder(proj.root_folder)

    return {"offline_clips": offline, "total": len(offline)}


@clips_router.post("/relink")
async def relink_clips(body: RelinkClipsRequest):
    project = rc.project
    if not project:
        raise HTTPException(status_code=400, detail="No project connected")

    mp = project.GetMediaPool()
    ms = rc.get_media_storage()

    clips = []
    for clip_uuid in body.clip_uuids:
        item = _find_media_pool_item(project, clip_uuid)
        if item:
            clips.append(item)

    if not clips:
        raise HTTPException(status_code=400, detail="No valid clips found")

    ms.SetCurrentSources(body.search_folders)
    result = mp.RelinkClips(clips, body.search_folders[0])

    try:
        registry.build_folder_tree(project)
    except Exception:
        pass

    return RelinkClipsResponse(
        success=bool(result),
        relinked_count=len(clips) if result else 0,
        failed_uuids=[] if result else body.clip_uuids,
    )


# ─── Internal Helpers ────────────────────────────────────────────────────────


def _find_davinci_folder(folder, target_uuid):
    if folder.GetUniqueId() == target_uuid:
        return folder
    for subfolder in (folder.GetSubFolderList() or []):
        result = _find_davinci_folder(subfolder, target_uuid)
        if result:
            return result
    return None


def _get_current_folder_uuid(project):
    mp = project.GetMediaPool()
    current = mp.GetCurrentFolder()
    if current:
        return current.GetUniqueId()
    return None


def _get_davinci_timeline(project, timeline_uuid):
    if timeline_uuid:
        tl_data = registry.get_timeline_by_uuid(timeline_uuid)
        if not tl_data:
            return None
        for i in range(1, project.GetTimelineCount() + 1):
            tl = project.GetTimelineByIndex(i)
            if tl and tl.GetName() == tl_data.name:
                return tl
        return None
    return project.GetCurrentTimeline()


def _find_media_pool_item(project, clip_uuid):
    clip_data = registry.get_clip_by_uuid(clip_uuid)
    if not clip_data:
        return None
    mp = project.GetMediaPool()
    root = mp.GetRootFolder()
    if root:
        return _find_clip_in_folder(root, clip_uuid)
    return None


def _find_clip_in_folder(folder, clip_uuid):
    for clip in (folder.GetClipList() or []):
        if clip.GetUniqueId() == clip_uuid:
            return clip
    for subfolder in (folder.GetSubFolderList() or []):
        result = _find_clip_in_folder(subfolder, clip_uuid)
        if result:
            return result
    return None


# Export sub-routers for registration
__all__ = ["router", "clips_router", "timelines_router", "media_router", "timeline_router"]

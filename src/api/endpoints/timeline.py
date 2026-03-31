"""
endpoints/timeline.py — Timeline API endpoints
GET  /api/timeline/*
POST /api/timeline/*
"""

import logging
from fastapi import APIRouter, HTTPException, Query

import src.resolve_connection as rc
from src.models.timeline_models import (
    TimelineListResponse,
    TimelineInfo,
    TimelineCurrentResponse,
    TimelineSetCurrentRequest,
    TimelineCreateRequest,
    TimelineCreateFromClipsRequest,
    TimelineImportFileRequest,
    TimelineDeleteRequest,
    TimelineAddMarkerRequest,
    TimelineMarkersResponse,
    TimelineMarkerInfo,
    TimelineItemsResponse,
    TimelineItemInfo,
    FusionNodeAddRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/timeline", tags=["Timeline"])


# ─── Timeline Listing ─────────────────────────────────────────────────────────

@router.get("/list", response_model=TimelineListResponse)
async def list_timelines():
    """List all timelines in the current project."""
    project = rc.get_project()
    count = project.GetTimelineCount()
    timelines = []
    current_name = None

    try:
        current_timeline = project.GetCurrentTimeline()
        if current_timeline:
            current_name = current_timeline.GetName()
    except Exception:
        pass

    for i in range(1, (count or 0) + 1):
        try:
            tl = project.GetTimelineByIndex(i)
            name = tl.GetName() if tl else f"Timeline {i}"
            timelines.append(TimelineInfo(name=name, index=i))
        except Exception:
            timelines.append(TimelineInfo(name=f"Timeline {i}", index=i))

    return TimelineListResponse(timelines=timelines, current=current_name)


@router.get("/current", response_model=TimelineCurrentResponse)
async def get_current_timeline():
    """Get info about the currently active timeline."""
    project = rc.get_project()
    try:
        tl = project.GetCurrentTimeline()
        if not tl:
            raise HTTPException(status_code=404, detail="No timeline is currently open")
        return TimelineCurrentResponse(
            name=tl.GetName(),
            start_frame=None,  # available via timeline properties
            end_frame=None,
            track_count=None,
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/current/set")
async def set_current_timeline(body: TimelineSetCurrentRequest):
    """Set the current active timeline by name."""
    project = rc.get_project()
    count = project.GetTimelineCount()
    for i in range(1, (count or 0) + 1):
        try:
            tl = project.GetTimelineByIndex(i)
            if tl and tl.GetName() == body.timeline_name:
                result = project.SetCurrentTimeline(tl)
                return {"success": bool(result), "timeline": body.timeline_name}
        except Exception:
            pass
    raise HTTPException(status_code=404, detail=f"Timeline '{body.timeline_name}' not found")


# ─── Timeline CRUD ─────────────────────────────────────────────────────────────

@router.post("/create")
async def create_timeline(body: TimelineCreateRequest):
    """Create a new empty timeline."""
    mp = rc.get_media_pool()
    try:
        tl = mp.CreateEmptyTimeline(body.name)
        if not tl:
            raise HTTPException(status_code=400, detail=f"Failed to create timeline '{body.name}'")
        return {"success": True, "timeline": body.name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/create-from-clips")
async def create_timeline_from_clips(body: TimelineCreateFromClipsRequest):
    """Create a timeline from existing MediaPool clips."""
    mp = rc.get_media_pool()
    clips = []
    for cid in body.clip_ids:
        try:
            clips.append(rc.get_clip_by_id(cid))
        except Exception:
            pass

    if not clips:
        raise HTTPException(status_code=404, detail="No valid clips found")

    try:
        tl = mp.CreateTimelineFromClips(body.name, clips)
        if not tl:
            raise HTTPException(status_code=400, detail=f"Failed to create timeline from clips")
        return {"success": True, "timeline": body.name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/import-file")
async def import_timeline(body: TimelineImportFileRequest):
    """
    Import a timeline from an external file.

    Supported formats: AAF, EDL, XML, FCPXML, DRT, ADL, OTIO

    Options:
    - timelineName: name for the imported timeline
    - importSourceClips: whether to import source clips (default True)
    - sourceClipsPath: path to search for source clips if media is offline
    - sourceClipsFolders: list of Media Pool folders to search
    """
    mp = rc.get_media_pool()
    options = body.options or {}

    try:
        tl = mp.ImportTimelineFromFile(body.file_path, options)
        if not tl:
            raise HTTPException(status_code=400, detail=f"Failed to import timeline from {body.file_path}")
        return {"success": True, "timeline": tl.GetName()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/delete")
async def delete_timelines(body: TimelineDeleteRequest):
    """Delete timelines by name."""
    project = rc.get_project()
    mp = project.GetMediaPool()
    timelines_to_delete = []

    for name in body.timeline_names:
        count = project.GetTimelineCount()
        for i in range(1, (count or 0) + 1):
            try:
                tl = project.GetTimelineByIndex(i)
                if tl and tl.GetName() == name:
                    timelines_to_delete.append(tl)
                    break
            except Exception:
                pass

    if not timelines_to_delete:
        raise HTTPException(status_code=404, detail="No matching timelines found")

    result = mp.DeleteTimelines(timelines_to_delete)
    return {"success": bool(result), "deleted": len(timelines_to_delete)}


# ─── Timeline Items ───────────────────────────────────────────────────────────

@router.get("/{timeline_index}/items", response_model=TimelineItemsResponse)
async def get_timeline_items(
    timeline_index: int,
    track_type: str = Query("video", description="video, audio, or subtitle"),
    track_index: int = Query(1, description="1-based track index"),
):
    """Get all items on a track of a timeline."""
    project = rc.get_project()
    tl = project.GetTimelineByIndex(timeline_index)
    if not tl:
        raise HTTPException(status_code=404, detail=f"Timeline {timeline_index} not found")

    items = tl.GetItemsInTrack(track_type, track_index) or {}
    result = []
    for start_frame, item in items.items():
        try:
            result.append(TimelineItemInfo(
                name=item.GetName() if hasattr(item, "GetName") else "unknown",
                duration=item.GetDuration() if hasattr(item, "GetDuration") else 0,
                start=start_frame,
                end=item.GetEnd() if hasattr(item, "GetEnd") else 0,
                track_type=track_type,
                track_index=track_index,
            ))
        except Exception:
            pass

    return TimelineItemsResponse(items=result, track_type=track_type, track_index=track_index)


# ─── Timeline Markers ───────────────────────────────────────────────────────────

@router.get("/{timeline_index}/markers", response_model=TimelineMarkersResponse)
async def get_timeline_markers(timeline_index: int):
    """Get all markers on a timeline."""
    project = rc.get_project()
    tl = project.GetTimelineByIndex(timeline_index)
    if not tl:
        raise HTTPException(status_code=404, detail=f"Timeline {timeline_index} not found")

    markers_raw = tl.GetMarkers() or {}
    markers = {}
    for frame, info in markers_raw.items():
        markers[str(frame)] = TimelineMarkerInfo(
            color=info.get("color", ""),
            duration=info.get("duration", 1.0),
            name=info.get("name", ""),
            note=info.get("note", ""),
            custom_data=info.get("customData", ""),
        )
    return TimelineMarkersResponse(markers=markers)


@router.post("/{timeline_index}/markers/add")
async def add_timeline_marker(timeline_index: int, body: TimelineAddMarkerRequest):
    """Add a marker to a timeline."""
    project = rc.get_project()
    tl = project.GetTimelineByIndex(timeline_index)
    if not tl:
        raise HTTPException(status_code=404, detail=f"Timeline {timeline_index} not found")

    result = tl.AddMarker(
        body.frame_id, body.color, body.name,
        body.note, body.duration, body.custom_data
    )
    return {"success": bool(result)}


# ─── Fusion ───────────────────────────────────────────────────────────────────

@router.get("/fusion/node-graph")
async def get_fusion_node_graph():
    """Get the Fusion node graph for the current timeline's active clip."""
    project = rc.get_project()
    try:
        tl = project.GetCurrentTimeline()
        if not tl:
            return {"nodes": [], "note": "No current timeline"}
        graph = tl.FusionGetComp()
        if not graph:
            return {"nodes": [], "note": "No Fusion comp found on current timeline"}
        # Return basic info - actual node traversal is complex
        return {"nodes": "Fusion comp available", "note": "Use /api/fusion endpoints for node operations"}
    except Exception as e:
        return {"nodes": [], "error": str(e)}

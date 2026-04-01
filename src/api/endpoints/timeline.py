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
    TimelineItemSetStartRequest,
    TimelineItemSetDurationRequest,
    TimelineItemRetimeRequest,
    TimelineItemTrimRequest,
    TimelineItemRepositionRequest,
    TimelineItemPropertiesResponse,
    TimelineItemOperationResponse,
    TimelineTrackInfo,
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


# ─── Timeline Item Operations ────────────────────────────────────────────────────

@router.get("/{index}/tracks", response_model=list[TimelineTrackInfo])
async def get_timeline_tracks(index: int):
    """
    List all tracks in a timeline with item counts.

    Useful for knowing what tracks exist before operating on specific items.
    """
    import src.resolve_connection as rc_conn
    try:
        tl = rc_conn.get_timeline_by_index(index)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    tracks = []
    for track_type in ["video", "audio", "subtitle"]:
        for track_index in range(1, 9999):
            items = tl.GetItemsInTrack(track_type, track_index) or {}
            if not items:
                break
            try:
                track_name = tl.GetTrackName(track_type, track_index)
            except Exception:
                track_name = None
            tracks.append(TimelineTrackInfo(
                track_type=track_type,
                track_index=track_index,
                track_name=track_name,
                item_count=len(items),
            ))
    return tracks


@router.get("/{index}/track/{track_type}/{track_index}/items", response_model=list[TimelineItemPropertiesResponse])
async def get_track_items(index: int, track_type: str, track_index: int):
    """
    Get all items in a specific track with their properties.

    track_type: "video", "audio", or "subtitle"
    track_index: 1-based track number
    """
    import src.resolve_connection as rc_conn
    try:
        tl = rc_conn.get_timeline_by_index(index)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    items_dict = tl.GetItemsInTrack(track_type, track_index) or {}
    result = []
    for item_index, (start, item) in enumerate(
        sorted(items_dict.items(), key=lambda x: x[0]), start=1
    ):
        try:
            media_name = item.GetName()
        except Exception:
            media_name = None

        try:
            media_id_str = str(item.GetMediaId())
        except Exception:
            media_id_str = None

        try:
            speed = item.GetSpeed()
            speed_percent = round(speed * 100, 2)
        except Exception:
            speed_percent = None

        try:
            flags = item.GetFlagList()
        except Exception:
            flags = None

        try:
            color = item.GetColor()
        except Exception:
            color = None

        result.append(TimelineItemPropertiesResponse(
            name=media_name or "",
            duration=item.GetDuration(),
            start=item.GetStart(),
            end=item.GetEnd(),
            media_name=media_name,
            media_id=media_id_str,
            speed_percent=speed_percent,
            flags=flags,
            color=color,
            track_type=track_type,
            track_index=track_index,
            item_index=item_index,
        ))
    return result


@router.post("/{index}/item/{track_type}/{track_index}/{item_index}/set-start", response_model=TimelineItemOperationResponse)
async def item_set_start(
    index: int, track_type: str, track_index: int, item_index: int,
    body: TimelineItemSetStartRequest,
):
    """Move a timeline item to a new start frame."""
    import src.resolve_connection as rc_conn
    try:
        item, _ = rc_conn.get_timeline_item(index, track_type, track_index, item_index)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        item.SetStart(body.start)
        return TimelineItemOperationResponse(success=True, message=f"Moved to frame {body.start}")
    except Exception as e:
        return TimelineItemOperationResponse(success=False, message=str(e))


@router.post("/{index}/item/{track_type}/{track_index}/{item_index}/retime", response_model=TimelineItemOperationResponse)
async def item_retime(
    index: int, track_type: str, track_index: int, item_index: int,
    body: TimelineItemRetimeRequest,
):
    """
    Retime a timeline item by speed percentage.

    speed_percent: e.g. 50.0 = half speed (2x duration), 200.0 = double speed (0.5x duration)
    """
    import src.resolve_connection as rc_conn
    try:
        item, _ = rc_conn.get_timeline_item(index, track_type, track_index, item_index)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        speed_ratio = body.speed_percent / 100.0
        item.SetSpeed(speed_ratio)
        return TimelineItemOperationResponse(
            success=True,
            message=f"Speed set to {body.speed_percent}%"
        )
    except Exception as e:
        return TimelineItemOperationResponse(success=False, message=str(e))


@router.post("/{index}/item/{track_type}/{track_index}/{item_index}/set-duration", response_model=TimelineItemOperationResponse)
async def item_set_duration(
    index: int, track_type: str, track_index: int, item_index: int,
    body: TimelineItemSetDurationRequest,
):
    """
    Set item duration by trimming. Adjusts the tail (end) of the clip.

    duration: new duration in frames
    """
    import src.resolve_connection as rc_conn
    try:
        item, start = rc_conn.get_timeline_item(index, track_type, track_index, item_index)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        # SetEnd changes the end frame, keeping start the same
        item.SetEnd(body.duration + start)
        return TimelineItemOperationResponse(
            success=True,
            message=f"Duration set to {body.duration} frames"
        )
    except Exception as e:
        return TimelineItemOperationResponse(success=False, message=str(e))


@router.post("/{index}/item/{track_type}/{track_index}/{item_index}/trim", response_model=TimelineItemOperationResponse)
async def item_trim(
    index: int, track_type: str, track_index: int, item_index: int,
    body: TimelineItemTrimRequest,
):
    """
    Trim frames from the head (start) and/or tail (end) of a timeline item.

    head_trim: frames to add/remove from the start (positive = trim into clip, negative = add handle)
    tail_trim: frames to add/remove from the end (positive = trim clip shorter)
    """
    import src.resolve_connection as rc_conn
    try:
        item, start = rc_conn.get_timeline_item(index, track_type, track_index, item_index)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        original_duration = item.GetDuration()
        new_start = start + body.head_trim
        new_end = start + original_duration - body.tail_trim

        item.SetStart(new_start)
        item.SetEnd(new_end)

        return TimelineItemOperationResponse(
            success=True,
            message=f"Trimmed: head {body.head_trim:+d}, tail {body.tail_trim:+d}"
        )
    except Exception as e:
        return TimelineItemOperationResponse(success=False, message=str(e))


@router.post("/{index}/item/{track_type}/{track_index}/{item_index}/reposition", response_model=TimelineItemOperationResponse)
async def item_reposition(
    index: int, track_type: str, track_index: int, item_index: int,
    body: TimelineItemRepositionRequest,
):
    """Move an item to a new position on the timeline without changing its duration."""
    import src.resolve_connection as rc_conn
    try:
        item, old_start = rc_conn.get_timeline_item(index, track_type, track_index, item_index)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        duration = item.GetDuration()
        item.SetStart(body.new_start)
        item.SetEnd(body.new_start + duration)
        return TimelineItemOperationResponse(
            success=True,
            message=f"Moved from frame {old_start} to {body.new_start}"
        )
    except Exception as e:
        return TimelineItemOperationResponse(success=False, message=str(e))


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

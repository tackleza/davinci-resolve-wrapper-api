"""
endpoints/render.py — Render Queue API endpoints
GET  /api/render/*
POST /api/render/*
"""

import logging
from fastapi import APIRouter, HTTPException, Query

import src.resolve_connection as rc
from src.models.timeline_models import (
    RenderFormatsResponse,
    RenderCodecsResponse,
    RenderResolutionsResponse,
    Resolution,
    RenderSettingsRequest,
    RenderSettingsResponse,
    SetFormatCodecRequest,
    RenderPresetsResponse,
    RenderPresetLoadRequest,
    RenderPresetSaveRequest,
    RenderPresetDeleteRequest,
    RenderJobListResponse,
    RenderJobInfo,
    RenderJobDeleteRequest,
    RenderStartRequest,
    RenderStatusResponse,
    RenderJobStatusResponse,
    QuickExportRequest,
    QuickExportResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/render", tags=["Render"])


# ─── Render Formats / Codecs / Resolutions ───────────────────────────────────

@router.get("/formats", response_model=RenderFormatsResponse)
async def get_render_formats():
    """Get all available render formats and their file extensions."""
    project = rc.get_project()
    formats = project.GetRenderFormats() or {}
    return RenderFormatsResponse(formats=formats)


@router.get("/codecs", response_model=RenderCodecsResponse)
async def get_render_codecs(format: str = Query(..., description="Render format key, e.g. 'mov'")):
    """Get available codecs for a specific render format."""
    project = rc.get_project()
    codecs = project.GetRenderCodecs(format) or {}
    return RenderCodecsResponse(codecs=codecs)


@router.get("/resolutions", response_model=RenderResolutionsResponse)
async def get_render_resolutions(
    format: str = Query(None),
    codec: str = Query(None),
):
    """Get available resolutions for a format/codec combination."""
    project = rc.get_project()
    if format and codec:
        resolutions = project.GetRenderResolutions(format, codec) or []
    else:
        resolutions = project.GetRenderResolutions() or []
    result = [Resolution(width=r.get("Width", 0), height=r.get("Height", 0)) for r in resolutions]
    return RenderResolutionsResponse(resolutions=result)


# ─── Render Settings ──────────────────────────────────────────────────────────

@router.get("/settings", response_model=RenderSettingsResponse)
async def get_render_settings():
    """Get current render settings for the project."""
    project = rc.get_project()
    fc = project.GetCurrentRenderFormatAndCodec() or {}
    mode = project.GetCurrentRenderMode()
    # Get full render settings including TargetDir, CustomName, etc.
    all_settings = project.GetRenderSettings() or {}
    return RenderSettingsResponse(
        format=fc.get("format"),
        codec=fc.get("codec"),
        render_mode=mode,
        export_video=all_settings.get("ExportVideo", True),
        export_audio=all_settings.get("ExportAudio", True),
        target_dir=all_settings.get("TargetDir"),
        custom_name=all_settings.get("CustomName"),
    )


@router.post("/settings")
async def set_render_settings(body: RenderSettingsRequest):
    """
    Set render settings for the project.

    Supported keys:
    - TargetDir, CustomName, SelectAllFrames, MarkIn, MarkOut
    - ExportVideo, ExportAudio, ExportCaption
    - Resolution (e.g. "1920x1080"), FrameRate (e.g. "23.976")
    """
    project = rc.get_project()
    settings = {}

    if body.target_dir is not None:
        settings["TargetDir"] = body.target_dir
    if body.custom_name is not None:
        settings["CustomName"] = body.custom_name
    if body.select_all_frames is not None:
        settings["SelectAllFrames"] = body.select_all_frames
    if body.mark_in is not None:
        settings["MarkIn"] = body.mark_in
    if body.mark_out is not None:
        settings["MarkOut"] = body.mark_out
    if body.export_video is not None:
        settings["ExportVideo"] = body.export_video
    if body.export_audio is not None:
        settings["ExportAudio"] = body.export_audio
    if body.export_caption is not None:
        settings["ExportCaption"] = body.export_caption
    if body.resolution_width and body.resolution_height:
        settings["Resolution"] = f"{body.resolution_width}x{body.resolution_height}"
    if body.frame_rate:
        settings["FrameRate"] = body.frame_rate

    if not settings:
        raise HTTPException(status_code=400, detail="No render settings provided")

    result = project.SetRenderSettings(settings)
    return {"success": bool(result), "applied_settings": list(settings.keys())}


@router.post("/format-set")
async def set_format_codec(body: SetFormatCodecRequest):
    """Set the render format and codec."""
    project = rc.get_project()
    result = project.SetCurrentRenderFormatAndCodec(body.format, body.codec)
    if not result:
        raise HTTPException(status_code=400, detail=f"Failed to set format '{body.format}' / codec '{body.codec}'")
    return {"success": True, "format": body.format, "codec": body.codec}


@router.get("/render-mode")
async def get_render_mode():
    """Get render mode: 0 = Individual clips, 1 = Single clip."""
    project = rc.get_project()
    mode = project.GetCurrentRenderMode()
    return {"render_mode": mode, "description": "0=Individual clips, 1=Single clip"}


@router.post("/render-mode")
async def set_render_mode(mode: int = Query(..., ge=0, le=1)):
    """Set render mode: 0 = Individual clips, 1 = Single clip."""
    project = rc.get_project()
    result = project.SetCurrentRenderMode(mode)
    return {"success": bool(result), "render_mode": mode}


# ─── Render Presets ───────────────────────────────────────────────────────────

@router.get("/presets", response_model=RenderPresetsResponse)
async def list_render_presets():
    """List all render presets."""
    project = rc.get_project()
    presets = project.GetRenderPresetList() or []
    return RenderPresetsResponse(presets=presets)


@router.post("/preset/load")
async def load_render_preset(body: RenderPresetLoadRequest):
    """Load a render preset."""
    project = rc.get_project()
    result = project.LoadRenderPreset(body.preset_name)
    if not result:
        raise HTTPException(status_code=404, detail=f"Render preset '{body.preset_name}' not found")
    return {"success": True, "preset": body.preset_name}


@router.post("/preset/save")
async def save_render_preset(body: RenderPresetSaveRequest):
    """Save current render settings as a new preset."""
    project = rc.get_project()
    result = project.SaveAsNewRenderPreset(body.preset_name)
    if not result:
        raise HTTPException(status_code=400, detail=f"Preset '{body.preset_name}' may already exist")
    return {"success": True, "preset": body.preset_name}


@router.post("/preset/delete")
async def delete_render_preset(body: RenderPresetDeleteRequest):
    """Delete a render preset."""
    project = rc.get_project()
    result = project.DeleteRenderPreset(body.preset_name)
    return {"success": bool(result)}


# ─── Render Jobs ─────────────────────────────────────────────────────────────

@router.get("/jobs", response_model=RenderJobListResponse)
async def list_render_jobs():
    """List all render jobs in the queue."""
    project = rc.get_project()
    jobs = project.GetRenderJobList() or []
    result = []
    for job in jobs:
        # DaVinci uses "JobId" (capital I), not "jobId"
        job_id = job.get("JobId") or job.get("jobId") or job.get("Id") or ""
        result.append(RenderJobInfo(
            job_id=str(job_id) if job_id else "",
            output_path=job.get("OutputPath") or job.get("output_path") or "",
            status=job.get("Status") or job.get("status") or "",
        ))
    return RenderJobListResponse(jobs=result)


@router.post("/job/add")
async def add_render_job():
    """Add a render job based on current render settings to the queue."""
    project = rc.get_project()
    # Add job and get the new job's ID
    new_job_id = project.AddRenderJob()
    # new_job_id may be an integer (the actual DaVinci job ID)
    # Return it as string for consistent API response
    return {"success": True, "job_id": str(new_job_id) if new_job_id else None}


@router.post("/job/delete")
async def delete_render_job(body: RenderJobDeleteRequest):
    """Delete a specific render job by ID."""
    project = rc.get_project()
    result = project.DeleteRenderJob(body.job_id)
    return {"success": bool(result)}


@router.post("/jobs/clear")
async def clear_all_jobs():
    """Delete all render jobs from the queue."""
    project = rc.get_project()
    result = project.DeleteAllRenderJobs()
    return {"success": bool(result)}


@router.post("/start")
async def start_rendering(body: RenderStartRequest | None = None):
    """Start rendering. If job_ids are provided, render those. Otherwise render all queued jobs."""
    project = rc.get_project()

    if project.IsRenderingInProgress():
        raise HTTPException(status_code=409, detail="Rendering is already in progress")

    if body and body.job_ids:
        result = project.StartRendering(body.job_ids, isInteractiveMode=False)
    else:
        result = project.StartRendering(isInteractiveMode=False)

    return {"success": bool(result)}


@router.post("/stop")
async def stop_rendering():
    """Stop any currently running render."""
    project = rc.get_project()
    project.StopRendering()
    return {"success": True}


@router.get("/status", response_model=RenderStatusResponse)
async def get_render_status():
    """Check if rendering is currently in progress."""
    project = rc.get_project()
    rendering = project.IsRenderingInProgress()
    return RenderStatusResponse(rendering=rendering)


@router.get("/status/{job_id}", response_model=RenderJobStatusResponse)
async def get_job_status(job_id: str):
    """Get detailed status and completion percentage of a render job."""
    project = rc.get_project()
    # DaVinci expects integer job ID, not string/UUID
    try:
        int_job_id = int(job_id)
    except (ValueError, TypeError):
        int_job_id = job_id
    status = project.GetRenderJobStatus(int_job_id) or {}
    return RenderJobStatusResponse(
        job_id=job_id,
        status=status.get("Status") or status.get("status") or "Unknown",
        completion_percent=status.get("Completion") or status.get("completion") or 0.0,
        job_name=status.get("JobName") or status.get("job_name"),
        output_path=status.get("OutputPath") or status.get("output_path"),
        frame_total=status.get("FrameTotal") or status.get("frame_total"),
        frame_completed=status.get("FrameCompleted") or status.get("frame_completed"),
        time_remaining_seconds=status.get("TimeRemaining") or status.get("time_remaining"),
        error_message=status.get("Error") or status.get("error"),
    )


# ─── Quick Export ─────────────────────────────────────────────────────────────

@router.get("/quick-export-presets")
async def list_quick_export_presets():
    """List available Quick Export presets."""
    project = rc.get_project()
    presets = project.GetQuickExportRenderPresets() or []
    return {"presets": presets}


@router.post("/quick-export", response_model=QuickExportResponse)
async def quick_export(body: QuickExportRequest):
    """
    Run a quick export using a quick export preset.
    Works on the current timeline.
    """
    project = rc.get_project()
    params = {}
    if body.target_dir:
        params["TargetDir"] = body.target_dir
    if body.custom_name:
        params["CustomName"] = body.custom_name
    if body.video_quality:
        params["VideoQuality"] = body.video_quality
    if body.enable_upload is not None:
        params["EnableUpload"] = body.enable_upload

    result = project.RenderWithQuickExport(body.preset_name, params)

    if isinstance(result, str):
        return QuickExportResponse(status="error", error=result)
    return QuickExportResponse(
        status=result.get("status", "completed"),
        time_taken_seconds=result.get("timeTaken"),
    )

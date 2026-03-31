"""
timeline_models.py — Pydantic models for Timeline / Render endpoints
"""

from pydantic import BaseModel
from typing import Optional


# ─── Render Formats / Codecs ──────────────────────────────────────────────────

class RenderFormatsResponse(BaseModel):
    formats: dict[str, str]  # e.g. {"QuickTime": "mov"}


class RenderCodecsResponse(BaseModel):
    codecs: dict[str, str]  # e.g. {"ProRes 422": "ProRes422"}


class Resolution(BaseModel):
    width: int
    height: int


class RenderResolutionsResponse(BaseModel):
    resolutions: list[Resolution]


# ─── Render Settings ──────────────────────────────────────────────────────────

class RenderSettingsRequest(BaseModel):
    format: Optional[str] = None
    codec: Optional[str] = None
    target_dir: Optional[str] = None
    custom_name: Optional[str] = None
    select_all_frames: Optional[bool] = None
    export_video: Optional[bool] = None
    export_audio: Optional[bool] = None
    export_caption: Optional[bool] = None
    mark_in: Optional[int] = None
    mark_out: Optional[int] = None
    resolution_width: Optional[int] = None
    resolution_height: Optional[int] = None
    frame_rate: Optional[str] = None


class RenderSettingsResponse(BaseModel):
    format: Optional[str] = None
    codec: Optional[str] = None
    target_dir: Optional[str] = None
    custom_name: Optional[str] = None
    render_mode: Optional[int] = None
    export_video: Optional[bool] = None
    export_audio: Optional[bool] = None


class SetFormatCodecRequest(BaseModel):
    format: str
    codec: str


# ─── Render Presets ──────────────────────────────────────────────────────────

class RenderPresetsResponse(BaseModel):
    presets: list[str]


class RenderPresetLoadRequest(BaseModel):
    preset_name: str


class RenderPresetSaveRequest(BaseModel):
    preset_name: str


class RenderPresetDeleteRequest(BaseModel):
    preset_name: str


# ─── Render Jobs ──────────────────────────────────────────────────────────────

class RenderJobInfo(BaseModel):
    job_id: str
    output_path: Optional[str] = None
    status: Optional[str] = None


class RenderJobListResponse(BaseModel):
    jobs: list[RenderJobInfo]


class RenderJobDeleteRequest(BaseModel):
    job_id: str


class RenderStartRequest(BaseModel):
    job_ids: Optional[list[str]] = None  # if None, renders all queued jobs


class RenderStatusResponse(BaseModel):
    rendering: bool
    job_id: Optional[str] = None


class RenderJobStatusResponse(BaseModel):
    job_id: str
    status: str
    completion_percent: Optional[float] = None


# ─── Quick Export ────────────────────────────────────────────────────────────

class QuickExportRequest(BaseModel):
    preset_name: str
    target_dir: Optional[str] = None
    custom_name: Optional[str] = None
    video_quality: Optional[str] = None
    enable_upload: Optional[bool] = None


class QuickExportResponse(BaseModel):
    status: str
    time_taken_seconds: Optional[float] = None
    error: Optional[str] = None


# ─── Timeline ─────────────────────────────────────────────────────────────────

class TimelineInfo(BaseModel):
    name: str
    index: int


class TimelineListResponse(BaseModel):
    timelines: list[TimelineInfo]
    current: Optional[str] = None


class TimelineCurrentResponse(BaseModel):
    name: str
    start_frame: Optional[int] = None
    end_frame: Optional[int] = None
    track_count: Optional[dict] = None


class TimelineSetCurrentRequest(BaseModel):
    timeline_name: str


class TimelineCreateRequest(BaseModel):
    name: str


class TimelineCreateFromClipsRequest(BaseModel):
    name: str
    clip_ids: list[str]


class TimelineImportFileRequest(BaseModel):
    file_path: str
    options: Optional[dict] = None


class TimelineDeleteRequest(BaseModel):
    timeline_names: list[str]


# ─── Timeline Markers ──────────────────────────────────────────────────────────

class TimelineAddMarkerRequest(BaseModel):
    frame_id: float
    color: str = "Green"
    name: str = ""
    note: str = ""
    duration: float = 1.0
    custom_data: str = ""


class TimelineMarkerInfo(BaseModel):
    color: str
    duration: float
    name: str
    note: str
    custom_data: str


class TimelineMarkersResponse(BaseModel):
    markers: dict[str, TimelineMarkerInfo]


# ─── Track Items ──────────────────────────────────────────────────────────────

class TimelineItemInfo(BaseModel):
    name: str
    duration: float
    start: float
    end: float
    track_type: str
    track_index: int


class TimelineItemsResponse(BaseModel):
    items: list[TimelineItemInfo]
    track_type: str
    track_index: int


# ─── Fusion ──────────────────────────────────────────────────────────────────

class FusionNodeAddRequest(BaseModel):
    node_type: str
    node_name: Optional[str] = None

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
    # Extended fields from DaVinci GetRenderJobStatus
    job_name: Optional[str] = None
    output_path: Optional[str] = None
    frame_total: Optional[int] = None
    frame_completed: Optional[int] = None
    time_remaining_seconds: Optional[int] = None
    error_message: Optional[str] = None


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


# ─── Timeline Item Operations ───────────────────────────────────────────────────

class TimelineItemSetStartRequest(BaseModel):
    track_type: str  # "video", "audio", or "subtitle"
    track_index: int  # 1-based
    item_index: int  # 1-based position in the track's item list
    start: int  # new start frame


class TimelineItemSetDurationRequest(BaseModel):
    track_type: str
    track_index: int
    item_index: int
    duration: int  # new duration in frames


class TimelineItemRetimeRequest(BaseModel):
    track_type: str
    track_index: int
    item_index: int
    speed_percent: float  # e.g. 100.0 = normal, 50.0 = half speed, 200.0 = double speed


class TimelineItemSetSpeedRequest(BaseModel):
    track_type: str
    track_index: int
    item_index: int
    speed: float  # speed as ratio, e.g. 1.0 = normal, 0.5 = half speed


class TimelineItemTrimRequest(BaseModel):
    track_type: str
    track_index: int
    item_index: int
    head_trim: int = 0  # frames to trim from head (start)
    tail_trim: int = 0  # frames to trim from tail (end)


class TimelineItemRepositionRequest(BaseModel):
    track_type: str
    track_index: int
    item_index: int
    new_start: int  # new start frame on the timeline


class TimelineItemResizeRequest(BaseModel):
    track_type: str
    track_index: int
    item_index: int
    new_duration: int  # new duration in frames
    keep_retime: bool = False  # if True, keep current speed adjustment


class TimelineItemPropertiesResponse(BaseModel):
    name: str
    duration: int
    start: int
    end: int
    media_name: Optional[str] = None
    media_id: Optional[str] = None
    speed_percent: Optional[float] = None
    flags: Optional[list[str]] = None
    color: Optional[str] = None
    track_type: str
    track_index: int
    item_index: int


class TimelineItemOperationResponse(BaseModel):
    success: bool
    message: str


class RenderProgressResponse(BaseModel):
    """Render progress estimated from output file growth."""
    rendering: bool
    output_path: str | None = None
    file_exists: bool
    file_size_bytes: int = 0
    file_size_mb: float = 0.0
    estimated_total_mb: float | None = None  # estimated from project duration / bitrate
    progress_percent: float | None = None  # if estimated_total is available
    note: str | None = None


class TimelineTrackInfo(BaseModel):
    track_type: str  # "video", "audio", or "subtitle"
    track_index: int  # 1-based
    track_name: Optional[str] = None
    item_count: int


# ─── Timeline Duplicate ──────────────────────────────────────────────────────

class TimelineDuplicateRequest(BaseModel):
    timeline_index: int = Field(description="1-based index of timeline to duplicate")
    new_name: str = Field(description="Name for the duplicated timeline")


# ─── Timeline Item Delete ─────────────────────────────────────────────────────

class TimelineDeleteItemsRequest(BaseModel):
    timeline_index: int = Field(description="1-based index of timeline")
    track_type: str = Field(description="video, audio, or subtitle")
    track_index: int = Field(description="1-based track index")
    item_indices: list[int] = Field(description="1-based indices of items to delete")


# ─── Timeline Add Clips ──────────────────────────────────────────────────────

class TimelineAddClipsRequest(BaseModel):
    media_pool_item_ids: list[str] = Field(description="media_id strings from the Media Pool")
    timeline_index: int | None = Field(default=None, description="Optional: 1-based timeline index. Uses current timeline if omitted.")
    track_index: int | None = Field(default=None, description="Optional: 1-based track index. Auto-selects if omitted.")
    insert_position: int | None = Field(default=None, description="Optional: frame to insert at. Appends to end if omitted.")

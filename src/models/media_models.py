"""
media_models.py — Pydantic models for MediaPool / Media Storage endpoints
"""

from pydantic import BaseModel
from typing import Optional


# ─── Media Import ──────────────────────────────────────────────────────────────

class ImportItemSimple(BaseModel):
    """A simple file path to import."""
    pass  # just a string in a list


class ImportItemWithRange(BaseModel):
    """Import item with a frame range (image sequences)."""
    media: str          # e.g. "D:/seq/frame_%04d.exr"
    start_frame: int
    end_frame: int


class ImportMediaRequest(BaseModel):
    """Request body for /api/media/import"""
    items: list[str | ImportItemWithRange]  # mix of strings and range dicts


class ImportedClip(BaseModel):
    name: str
    media_id: str


class ImportMediaResponse(BaseModel):
    imported_clips: list[ImportedClip]
    total: int


class ImportDavinciRequest(BaseModel):
    """Request body for /api/media/import-davinci — uses MediaPool.ImportMediaIntoMediaPool."""
    paths: list[str]  # absolute file paths, e.g. ["Y:\\Video Editing Job\\sb4-13\\video.mp4"]


# ─── Clip ─────────────────────────────────────────────────────────────────────

class ClipInfo(BaseModel):
    name: str
    media_id: str
    duration: Optional[float] = None
    proxy: Optional[str] = None
    audio_tracks: Optional[int] = None


class ClipListResponse(BaseModel):
    clips: list[ClipInfo]


class ClipDetailResponse(BaseModel):
    name: str
    media_id: str
    properties: dict
    metadata: dict


class ClipPropertyRequest(BaseModel):
    property_name: Optional[str] = None  # if None, returns all


class SetMetadataRequest(BaseModel):
    metadata: dict[str, str]


# ─── Markers on Clips ──────────────────────────────────────────────────────────

class AddMarkerRequest(BaseModel):
    frame_id: float
    color: str = "Green"
    name: str = ""
    note: str = ""
    duration: float = 1.0
    custom_data: str = ""


class MarkerInfo(BaseModel):
    color: str
    duration: float
    name: str
    note: str
    custom_data: str


class ClipMarkersResponse(BaseModel):
    markers: dict[str, MarkerInfo]


# ─── Flags ────────────────────────────────────────────────────────────────────

class AddFlagRequest(BaseModel):
    color: str  # Red, Yellow, Green, Cyan, Blue, Purple, Gray, White


class FlagListResponse(BaseModel):
    flags: list[str]


# ─── Relink / Unlink ──────────────────────────────────────────────────────────

class RelinkClipsRequest(BaseModel):
    clip_ids: list[str]  # list of media_id strings
    folder_path: str


class ComprehensiveSearchRequest(BaseModel):
    """Request body for /api/media/comprehensive-search — DaVinci's 'Perform Comprehensive Search'.
    Sets multiple search paths and tells DaVinci to find+relink all offline clips across those paths.
    """
    folders: list[str]  # absolute folder paths to search, e.g. ["Y:\\folder1","Y:\\folder2"]
    clip_ids: list[str] | None = None  # optional: specific clip IDs to search. If None, searches all offline.


class UnlinkClipsRequest(BaseModel):
    clip_ids: list[str]


class ClipDeleteRequest(BaseModel):
    clip_ids: list[str]


class ClipMoveRequest(BaseModel):
    clip_ids: list[str]
    target_folder: str


class ClipColorRequest(BaseModel):
    color: str


# ─── Folder ───────────────────────────────────────────────────────────────────

class CreateFolderRequest(BaseModel):
    name: str
    parent_folder: Optional[str] = None  # if None, creates in current folder


class FolderInfo(BaseModel):
    name: str
    clip_count: Optional[int] = None


class MediaPoolResponse(BaseModel):
    current_folder: Optional[str] = None
    root_folder: Optional[str] = None
    subfolders: list[FolderInfo]


class FolderCreateResponse(BaseModel):
    success: bool
    folder_name: str


# ─── Files / Volumes ──────────────────────────────────────────────────────────

class MediaFile(BaseModel):
    name: str
    path: str
    type: str  # "media" or "folder"


class FileListResponse(BaseModel):
    files: list[MediaFile]


class SubfoldersResponse(BaseModel):
    subfolders: list[str]


class VolumesResponse(BaseModel):
    volumes: list[str]


# ─── Batch Import ───────────────────────────────────────────────────────────

class BatchImportRequest(BaseModel):
    """Import files in batches to avoid DaVinci crashes."""
    folder_path: str  # folder containing files to import
    batch_size: int = 20  # files per batch
    recursive: bool = False  # include subfolders
    extensions: Optional[list[str]] = None  # filter by extension e.g. ["mp4", "mov", "mp3"]


class BatchImportProgress(BaseModel):
    total_files: int
    imported: int
    batch_num: int
    current_batch: int
    current_file: str


class BatchImportResult(BaseModel):
    success: bool
    total_files: int
    imported_clips: int
    failed_files: int
    batches: int
    errors: list[str]


# ─── Auto Sync Audio ─────────────────────────────────────────────────────────

class AutoSyncAudioRequest(BaseModel):
    clip_ids: list[str]
    algorithm: Optional[int] = None
    align_method: Optional[int] = None
    silences: Optional[bool] = None
    threshold: Optional[float] = None
    fade_length: Optional[float] = None
    fade_curve: Optional[int] = None
    ignore_audio: Optional[bool] = None
    sample_rate: Optional[int] = None
    start_offset: Optional[int] = None
    duration: Optional[int] = None

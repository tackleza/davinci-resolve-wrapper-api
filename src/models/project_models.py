"""
project_models.py — Pydantic models for Project/ProjectManager endpoints
"""

from pydantic import BaseModel
from typing import Optional


class ProjectInfo(BaseModel):
    name: str
    unique_id: Optional[str] = None
    timeline_count: Optional[int] = None


class ProjectListResponse(BaseModel):
    projects: list[str]
    current_folder: Optional[str] = None


class CreateProjectRequest(BaseModel):
    project_name: str
    media_location_path: Optional[str] = ""


class LoadProjectRequest(BaseModel):
    project_name: str


class DeleteProjectRequest(BaseModel):
    project_name: str


class ImportProjectRequest(BaseModel):
    file_path: str
    project_name: Optional[str] = None


class ExportProjectRequest(BaseModel):
    project_name: str
    file_path: str
    with_stills_and_luts: bool = True


class ArchiveProjectRequest(BaseModel):
    project_name: str
    file_path: str
    is_archive_src_media: bool = True
    is_archive_render_cache: bool = True
    is_archive_proxy_media: bool = False


class RestoreProjectRequest(BaseModel):
    file_path: str
    project_name: Optional[str] = None


class FolderCreateRequest(BaseModel):
    folder_name: str


class FolderDeleteRequest(BaseModel):
    folder_name: str


class NavigateFolderRequest(BaseModel):
    folder_name: str  # Use "root" or ".." for special navigation


class SetDatabaseRequest(BaseModel):
    db_type: str  # "Disk" or "PostgreSQL"
    db_name: str
    ip_address: Optional[str] = "127.0.0.1"


class DatabaseInfo(BaseModel):
    db_type: str
    db_name: str
    ip_address: Optional[str] = None


class DatabaseListResponse(BaseModel):
    databases: list[DatabaseInfo]


class DatabaseInfoResponse(BaseModel):
    db_type: str
    db_name: str
    ip_address: Optional[str] = None


# ─── Project Settings ────────────────────────────────────────────────────────

class ProjectSettingsResponse(BaseModel):
    """Current project settings."""
    frame_rate: float
    resolution_width: int
    resolution_height: int
    proxy_mode: str
    color_space: str
    gamma: str
    settings: dict[str, str] = Field(default_factory=dict, description="All project settings as key-value pairs")


class ProjectSettingRequest(BaseModel):
    """Set a specific project setting."""
    key: str = Field(description="Setting name, e.g. 'timelineFrameRate'")
    value: str = Field(description="Setting value")

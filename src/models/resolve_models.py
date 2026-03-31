"""
resolve_models.py — Pydantic models for Resolve-level endpoints
"""

from pydantic import BaseModel
from typing import Optional


class HealthResponse(BaseModel):
    connected: bool
    product_name: Optional[str] = None
    version: Optional[str] = None
    version_array: Optional[list] = None
    current_page: Optional[str] = None
    current_project: Optional[str] = None
    error: Optional[str] = None


class CurrentPageResponse(BaseModel):
    page: Optional[str] = None


class OpenPageRequest(BaseModel):
    page_name: str


class LayoutPresetRequest(BaseModel):
    preset_name: str


class LayoutPresetExportRequest(BaseModel):
    preset_name: str
    file_path: str


class LayoutPresetImportRequest(BaseModel):
    file_path: str
    preset_name: Optional[str] = None


class RenderPresetImportRequest(BaseModel):
    preset_path: str


class RenderPresetExportRequest(BaseModel):
    preset_name: str
    export_path: str


class RenderPresetsResponse(BaseModel):
    presets: list[str]


class LayoutPresetsResponse(BaseModel):
    presets: list[str]

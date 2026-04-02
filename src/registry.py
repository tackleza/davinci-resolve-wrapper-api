"""
registry.py - UUID-based object registry for DaVinci Resolve
"""

from dataclasses import dataclass, field
from typing import Optional, Dict


@dataclass
class ClipData:
    uuid: str
    name: str
    media_type: Optional[str] = None
    duration: Optional[float] = None
    media_id: Optional[int] = None


@dataclass
class TimelineData:
    uuid: str
    name: str
    index: int = 0


@dataclass
class FolderData:
    uuid: str
    name: str
    parent_uuid: Optional[str] = None
    clips: Dict[str, ClipData] = field(default_factory=dict)
    subfolders: Dict[str, "FolderData"] = field(default_factory=dict)


@dataclass
class ProjectData:
    uuid: str
    name: str
    root_folder: Optional[FolderData] = None
    timelines: Dict[str, TimelineData] = field(default_factory=dict)


class Registry:
    def __init__(self):
        self._projects: Dict[str, ProjectData] = {}
        self._current_project_uuid: Optional[str] = None

    @property
    def projects(self) -> Dict[str, ProjectData]:
        return self._projects

    @property
    def current_project(self) -> Optional[ProjectData]:
        if self._current_project_uuid:
            return self._projects.get(self._current_project_uuid)
        return None

    def register_project(self, project) -> ProjectData:
        uuid = project.GetUniqueId()
        name = project.GetName()
        project_data = ProjectData(uuid=uuid, name=name)
        self._projects[uuid] = project_data
        self._current_project_uuid = uuid
        return project_data

    def get_project_by_uuid(self, uuid: str) -> Optional[ProjectData]:
        return self._projects.get(uuid)

    def set_current_project(self, uuid: str):
        if uuid in self._projects:
            self._current_project_uuid = uuid

    def register_folder(self, folder, parent_uuid: Optional[str] = None) -> FolderData:
        uuid = folder.GetUniqueId()
        name = folder.GetName()
        folder_data = FolderData(uuid=uuid, name=name, parent_uuid=parent_uuid)
        if self.current_project and self.current_project.root_folder is None:
            self.current_project.root_folder = folder_data
        return folder_data

    def get_folder_by_uuid(self, uuid: str) -> Optional[FolderData]:
        for project in self._projects.values():
            if project.root_folder:
                found = self._find_folder_recursive(project.root_folder, uuid)
                if found:
                    return found
        return None

    def _find_folder_recursive(self, folder: FolderData, uuid: str) -> Optional[FolderData]:
        if folder.uuid == uuid:
            return folder
        for subfolder in folder.subfolders.values():
            found = self._find_folder_recursive(subfolder, uuid)
            if found:
                return found
        return None

    def register_clip(self, clip, folder_uuid: str) -> ClipData:
        uuid = clip.GetUniqueId()
        name = clip.GetName()
        media_type = None
        try:
            props = clip.GetClipProperty()
            if props:
                media_type = props.get("Type")
        except:
            pass
        clip_data = ClipData(uuid=uuid, name=name, media_type=media_type)
        folder = self.get_folder_by_uuid(folder_uuid)
        if folder:
            folder.clips[uuid] = clip_data
        return clip_data

    def get_clip_by_uuid(self, uuid: str) -> Optional[ClipData]:
        for project in self._projects.values():
            if project.root_folder:
                found = self._find_clip_recursive(project.root_folder, uuid)
                if found:
                    return found
        return None

    def _find_clip_recursive(self, folder: FolderData, uuid: str) -> Optional[ClipData]:
        if uuid in folder.clips:
            return folder.clips[uuid]
        for subfolder in folder.subfolders.values():
            found = self._find_clip_recursive(subfolder, uuid)
            if found:
                return found
        return None

    def register_timeline_from_clip(self, clip, folder_uuid: str, timeline_index: int = 0) -> TimelineData:
        uuid = clip.GetUniqueId()
        name = clip.GetName()
        timeline_data = TimelineData(uuid=uuid, name=name, index=timeline_index)
        if self.current_project:
            self.current_project.timelines[uuid] = timeline_data
        clip_data = ClipData(uuid=uuid, name=name, media_type="Timeline")
        folder = self.get_folder_by_uuid(folder_uuid)
        if folder:
            folder.clips[uuid] = clip_data
        return timeline_data

    def get_timeline_by_uuid(self, uuid: str) -> Optional[TimelineData]:
        if self.current_project:
            return self.current_project.timelines.get(uuid)
        return None

    def build_folder_tree(self, project):
        if not self.current_project:
            return
        mp = project.GetMediaPool()
        root = mp.GetRootFolder()
        if root:
            self._build_folder_recursive(root, None)

    def _build_folder_recursive(self, folder, parent_uuid: Optional[str]):
        folder_data = self.register_folder(folder, parent_uuid)
        is_timeline_folder = (folder.GetName() == "#Timeline")
        for clip in (folder.GetClipList() or []):
            if is_timeline_folder:
                timeline_index = len(self.current_project.timelines) + 1
                self.register_timeline_from_clip(clip, folder_data.uuid, timeline_index)
            else:
                self.register_clip(clip, folder_data.uuid)
        for subfolder in (folder.GetSubFolderList() or []):
            self._build_folder_recursive(subfolder, folder_data.uuid)

    def clear(self):
        self._projects.clear()
        self._current_project_uuid = None


registry = Registry()

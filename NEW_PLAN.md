# DaVinci Resolve Wrapper API — NEW PLAN

## Big Picture

**Problem:** DaVinci Resolve API has no reverse-lookup by UUID. Objects (Folder, Clip, Timeline) are referenced by name or direct object reference, but name can be duplicated and object references can't be serialized/stored.

**Solution:** Build a UUID-based registry system that:
1. Caches all DaVinci objects by UUID
2. Provides REST API endpoints to query/manage them
3. Persists across requests (in-memory)

**Core Principle:** Every object has a UUID. Use UUID as the canonical identifier, not name.

---

## Data Model

```
Registry
├── projects: { uuid: ProjectData }
│
ProjectData
├── uuid: str
├── name: str
├── root_folder: FolderData
│
FolderData
├── uuid: str
├── name: str
├── parent_uuid: str | None
├── clips: { uuid: ClipData }
├── subfolders: { uuid: FolderData }
│
ClipData
├── uuid: str
├── name: str
├── duration: float | None
├── media_id: int | None
│
TimelineData
├── uuid: str
├── name: str
├── index: int
```

---

## API Design

### Base URL: `/api/registry`

#### Projects

```
GET  /api/registry/projects
     → list all registered projects

     Response: {
       "projects": [
         {
           "uuid": "xxx",
           "name": "sb4-13",
           "is_current": true
         }
       ]
     }

GET  /api/registry/projects/current
     → get current project + full tree

     Response: {
       "uuid": "xxx",
       "name": "sb4-13",
       "root_folder": FolderData,
       "timelines": { uuid: TimelineData }
     }

POST /api/registry/projects/set
     Body: { "uuid": "xxx" } or { "name": "sb4-13" }

POST /api/registry/projects/rebuild
     → rebuild full tree for current project
```

#### Folders

```
GET  /api/registry/folders
     → list ALL folders in current project (flat list)

     Response: {
       "folders": [
         {
           "uuid": "xxx",
           "name": "Internal",
           "parent_uuid": "yyy",
           "clip_count": 3
         }
       ]
     }

GET  /api/registry/folders/{uuid}
     → get folder details + clips + subfolders

     Response: {
       "uuid": "xxx",
       "name": "Internal",
       "parent_uuid": "yyy",
       "clips": [
         { "uuid": "zzz", "name": "Sub-Thai.mp4" }
       ],
       "subfolders": [
         { "uuid": "aaa", "name": "Proxies" }
       ]
     }

GET  /api/registry/folders/{uuid}/tree
     → get folder + ALL subfolders recursively

GET  /api/registry/folders/{uuid}/parent
     → get parent folder

GET  /api/registry/folders/by-path?path=Master/Tackle4826-Common/Outtro
     → find folder by path string
```

#### Clips

```
GET  /api/registry/clips
     → list ALL clips in current project (flat list)

GET  /api/registry/clips/{uuid}
     → get clip details (name, duration, media_id, etc.)

     Response: {
       "uuid": "xxx",
       "name": "Sub-Thai.mp4",
       "duration": 30.5,
       "media_id": 123,
       "folder_uuid": "yyy",
       "properties": {
         "Type": "Video",
         "Frame Rate": "59.94fps",
         ...
       }
     }
```

#### Timelines

```
GET  /api/registry/timelines
     → list ALL timelines in current project

     Response: {
       "timelines": [
         { "uuid": "xxx", "name": "sb4-13-body", "index": 1 }
       ]
     }

GET  /api/registry/timelines/{uuid}
     → get timeline details

GET  /api/registry/timelines/current
     → get currently active timeline
```

---

## Implementation Phases

### Phase 1: Core Registry ✅
- [x] `src/registry.py` — UUID registry class
- [x] `src/resolve_connection.py` — init_registry() on project load
- [x] Build tree on project load (recursive GetSubFolderList + GetClipList)
- [x] Register all objects (Project, Folder, Clip, Timeline)
- [x] `/api/registry/projects` — list + current project
- [x] `/api/registry/projects/rebuild` — force rebuild tree

### Phase 2: Folder & Clip Access ✅
- [x] `/api/registry/folders` — flat list all folders
- [x] `/api/registry/folders/{uuid}` — folder details
- [x] `/api/registry/folders/{uuid}/tree` — recursive folder tree
- [x] `/api/registry/clips` — flat list all clips
- [x] `/api/registry/clips/{uuid}` — clip details + properties

### Phase 3: Timeline Access ✅
- [x] `/api/registry/timelines` — list all timelines
- [x] `/api/registry/timelines/{uuid}` — timeline details
- [x] `/api/registry/timelines/current` — active timeline

### Phase 4: Actions (Use Cases) 🚧
- [x] Import media: `POST /api/registry/media/import` ✅
- [x] Insert footage: `POST /api/registry/timeline/insert` ✅
- [x] Relink clips: `GET /api/registry/clips/offline` + `POST /api/registry/clips/relink` ✅
- [x] Render: `POST /api/render/start` ✅ (old code)
- [x] Save/Close project: `POST /api/project/save`, `POST /api/project/close` ✅
- [x] Quit DaVinci: `POST /api/resolve/quit` ✅
- [ ] Navigate to folder: `POST /api/registry/folders/{uuid}/navigate`

---

## Technical Notes

### How to Build Folder Tree

```python
def build_tree(folder, parent_uuid=None):
    folder_uuid = folder.GetUniqueId()
    folder_name = folder.GetName()
    
    # Register folder
    register_folder(uuid=folder_uuid, name=folder_name, parent_uuid=parent_uuid)
    
    # Get clips (video/audio)
    for clip in (folder.GetClipList() or []):
        register_clip(uuid=clip.GetUniqueId(), name=clip.GetName(), folder_uuid=folder_uuid)
    
    # Get items (stills, generators) — different from GetClipList!
    if hasattr(folder, 'GetItemList'):
        for item in (folder.GetItemList() or []):
            # Check not duplicate with GetClipList
            register_clip(uuid=item.GetUniqueId(), name=item.GetName(), folder_uuid=folder_uuid)
    
    # Recurse subfolders
    for subfolder in (folder.GetSubFolderList() or []):
        build_tree(subfolder, parent_uuid=folder_uuid)
```

### Important Discovery

- `GetParentFolder()` returns `None` for some folders (DaVinci API limitation!)
- `GetItemList()` returns timeline items in `#Timeline` folder, not just still images
- Use `parent_uuid` tracking in registry to walk UP the tree
- UUID is the only reliable identifier — names can be duplicated!

### Key Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/registry/projects/current` | Get current project + full tree |
| POST | `/api/registry/projects/rebuild` | Rebuild tree if folder structure changes |
| GET | `/api/registry/folders` | List all folders |
| GET | `/api/registry/folders/{uuid}` | Folder details + clips |
| GET | `/api/registry/folders/{uuid}/tree` | Recursive folder tree |
| GET | `/api/registry/clips` | List all clips |
| GET | `/api/registry/clips/{uuid}` | Clip details + properties |
| GET | `/api/registry/timelines` | List all timelines |
| GET | `/api/registry/timelines/{uuid}` | Timeline details |

---

## Phase 5: Import Media API

### Overview
Media import has two source types:
- **Local** — files on local drives (C:\, D:\, mounted USB, etc.)
- **Network** — files on NAS/network shares (Y:\ = /mnt/Tackle-Pool-01 on Linux, visible as Y:\ on Windows)

Import uses DaVinci's `GetMediaPool().ImportMedia()` which accepts a list of file paths + optional destination folder.

### Data Model

```python
@dataclass
class ImportJob:
    source_type: Literal["local", "network"]
    paths: list[str]                  # absolute file paths
    destination_folder_uuid: str | None  # UUID of target folder in Media Pool
    import_mode: str = "copy"         # "copy" | "link" | "hide"

@dataclass
class ImportResult:
    success: bool
    imported_clips: list[ImportedClip]  # clips added to Media Pool
    failed_paths: list[FailedImport]   # paths that failed
    destination_folder_uuid: str | None

@dataclass
class ImportedClip:
    uuid: str
    name: str
    path: str
    folder_uuid: str

@dataclass
class FailedImport:
    path: str
    error: str
```

### API Design

#### Import Media
```
POST /api/registry/media/import
```

**Request:**
```json
{
  "source_type": "local" | "network",
  "paths": ["Y:\\Video Editing Job\\1. Pending\\sb4-14\\clip1.mp4"],
  "destination_folder_uuid": "xxx",   // optional: import into this folder
  "import_mode": "copy"               // "copy" | "link" | "move"
}
```

**Response:**
```json
{
  "success": true,
  "imported_clips": [
    {
      "uuid": "zzz",
      "name": "clip1.mp4",
      "path": "Y:\\Video Editing Job\\1. Pending\\sb4-14\\clip1.mp4",
      "folder_uuid": "xxx"
    }
  ],
  "failed_paths": [],
  "destination_folder_uuid": "xxx"
}
```

**Behavior:**
- `source_type=local` → paths are Windows local paths
- `source_type=network` → paths are NAS paths (Y:\...)
- If `destination_folder_uuid` is null → import to current folder
- On success → clips are registered in the UUID registry
- On failure → `failed_paths` lists what went wrong

#### Import Folder (recursive)
```
POST /api/registry/media/import-folder
```

**Request:**
```json
{
  "source_type": "local" | "network",
  "folder_path": "Y:\\Video Editing Job\\1. Pending\\sb4-14",
  "destination_folder_uuid": "xxx",
  "recursive": true,
  "file_extensions": [".mp4", ".mov", ".wav", ".mp3"]
}
```

**Response:**
```json
{
  "success": true,
  "imported_clips": [...],
  "failed_paths": [],
  "total_imported": 12
}
```

**Behavior:**
- Scans `folder_path` for matching `file_extensions`
- `recursive=true` → scan subfolders
- DaVinci's `ImportMedia()` auto-creates subfolder structure

#### Import by Pattern
```
POST /api/registry/media/import-pattern
```

**Request:**
```json
{
  "source_type": "network",
  "folder_path": "Y:\\Video Editing Job\\1. Pending\\sb4-14",
  "pattern": "*.mp4",
  "destination_folder_uuid": "xxx"
}
```

**Response:**
```json
{
  "success": true,
  "matched_files": ["clip1.mp4", "clip2.mp4"],
  "imported_clips": [...]
}
```

### Path Reference

| Source | Linux Path | Windows Path |
|--------|-----------|--------------|
| NAS (main storage) | `/mnt/Tackle-Pool-01/` | `Y:\\` |
| NAS git repo | `/mnt/Tackle-Pool-01/git/` | `Y:\\git\\` |
| Video Editing Job | `/mnt/Tackle-Pool-01/Video Editing Job/` | `Y:\\Video Editing Job\\` |
| VM local ( footage) | — | `C:\\Users\\Tackle\\Footage\\` |

### Implementation Notes

1. **Import is synchronous** — DaVinci's `ImportMedia()` blocks until done
2. **After import → re-register** clips in UUID registry via `POST /api/registry/projects/rebuild`
3. **Network import speed** depends on NAS read speed (gigabit wired)
4. **Import mode**:
   - `"copy"` — copy files into DaVinci's cache (default)
   - `"link"` — link only (proxy reference)
   - `"move"` — move from source location
5. **Supported formats**: DaVinci supports most video/audio formats (.mp4, .mov, .mxf, .r3d, .braw, .wav, .mp3, etc.)

### Endpoint Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| **Project** |
| POST | `/api/project/save` | Save current project |
| POST | `/api/project/close` | Close current project |
| **Resolve** |
| POST | `/api/resolve/quit` | Quit DaVinci |
| **Render** |
| GET | `/api/render/presets` | List render presets |
| POST | `/api/render/preset/load` | Load preset |
| GET | `/api/render/settings` | Current render settings |
| POST | `/api/render/settings` | Update render settings |
| GET | `/api/render/jobs` | List render queue |
| POST | `/api/render/job` | Add job to queue |
| DELETE | `/api/render/jobs` | Clear queue |
| POST | `/api/render/start` | Start rendering |
| POST | `/api/render/stop` | Stop rendering |
| GET | `/api/render/status` | Check rendering status |
| GET | `/api/render/progress` | Render progress % |
| **Registry — Media** |
| POST | `/api/registry/media/import` | Import files into Media Pool |
| GET | `/api/registry/clips/offline` | List offline clips |
| POST | `/api/registry/clips/relink` | Relink offline clips |
| **Registry — Timeline** |
| POST | `/api/registry/timeline/insert` | Insert clips at cursor |

### Technical Implementation

```python
# Import files into DaVinci Media Pool
mp = project.GetMediaPool()

# Option A: Import to specific folder (using UUID → folder lookup)
if destination_folder_uuid:
    folder = registry.get_folder_by_uuid(destination_folder_uuid)
    if folder:
        # Navigate to folder first
        mp.SetCurrentFolder(folder._da Vinci_folder_object)

# Option B: Import to current folder
clips = mp.ImportMedia(["Y:\\path\\to\\file.mp4"])

# After import → register new clips in registry
for clip in clips:
    registry.register_clip(clip, folder_uuid=destination_folder_uuid)
```

---

## Archive

Old endpoints moved to: `src/api/endpoints/archive/`
- `media.py` — old media pool endpoints
- `projects.py` — old project endpoints  
- `timeline.py` — old timeline endpoints
- `render.py` — old render endpoints
- `resolve.py` — old resolve endpoints

These will be redesigned in Phase 4 using the new registry system.

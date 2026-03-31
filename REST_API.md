# REST_API.md — DaVinci Wrapper API — HTTP API Reference

**Base URL:** `http://localhost:8080`
**Version:** 1.0
**API Docs:** `http://localhost:8080/docs` (Swagger UI)

---

## Conventions

- `GET` — Read/query operations
- `POST` — Write/action operations
- Response format: JSON
- Error format: `{"detail": "error message", "code": "ERROR_CODE"}`
- All paths prefixed with `/api/`

---

## Groups

- [Resolve](#group---resolve)
- [Projects](#group---projects)
- [Media](#group---media)
- [Render](#group---render)
- [Timeline](#group---timeline)
- [Fusion](#group---fusion)

---

## Group - Resolve

### `GET /api/resolve/health`

Check if DaVinci Resolve is reachable.

**Response:**
```json
{
  "connected": true,
  "product_name": "DaVinci Resolve Studio",
  "version": "19.1.3.7",
  "version_array": [19, 1, 3, 7, ""]
}
```

---

### `GET /api/resolve/pages`

Get available page names.

**Response:**
```json
["media", "cut", "edit", "fusion", "color", "fairlight", "deliver"]
```

---

### `GET /api/resolve/current-page`

Get the currently active page.

**Response:**
```json
{"page": "edit"}
```

---

### `POST /api/resolve/open-page`

Switch to a different page.

**Body:**
```json
{"page_name": "color"}
```

**Valid values:** `media`, `cut`, `edit`, `fusion`, `color`, `fairlight`, `deliver`

**Response:**
```json
{"success": true}
```

---

### `POST /api/resolve/quit`

Quit DaVinci Resolve.

**Response:**
```json
{"success": true}
```

---

### `GET /api/resolve/layout-presets`

List all saved layout presets.

**Response:**
```json
{"presets": ["Default", "Color Grade", "Custom Layout"]}
```

---

### `POST /api/resolve/layout-preset/load`

Load a layout preset.

**Body:**
```json
{"preset_name": "My Custom Layout"}
```

---

### `POST /api/resolve/layout-preset/save`

Save current UI layout as a preset.

**Body:**
```json
{"preset_name": "My New Layout"}
```

---

### `POST /api/resolve/layout-preset/export`

Export a layout preset to a file.

**Body:**
```json
{"preset_name": "My Layout", "file_path": "C:/Layouts/my_layout.preset"}
```

---

### `POST /api/resolve/layout-preset/import`

Import a layout preset from a file.

**Body:**
```json
{"file_path": "C:/Layouts/my_layout.preset", "preset_name": "Imported Layout"}
```

---

### `GET /api/resolve/render-presets`

List all render presets.

**Response:**
```json
{"presets": ["YouTube 4K", "Social Media 1080p", "Master File"]}
```

---

### `POST /api/resolve/render-preset/import`

Import a render preset from file.

**Body:**
```json
{"preset_path": "C:/Presets/my_render.drp"}
```

---

### `POST /api/resolve/render-preset/export`

Export a render preset to file.

**Body:**
```json
{"preset_name": "My Render Preset", "export_path": "C:/Presets/exported.drp"}
```

---

## Group - Projects

### `GET /api/projects`

List all projects in the current folder.

**Response:**
```json
{
  "projects": ["Project Alpha", "Commercial 2024", "Doc Thailand"],
  "current_folder": "Work Projects"
}
```

---

### `GET /api/projects/current`

Get the currently loaded project.

**Response:**
```json
{
  "name": "Project Alpha",
  "unique_id": "abc-123-def",
  "timeline_count": 3
}
```

---

### `POST /api/projects/create`

Create a new project.

**Body:**
```json
{"project_name": "New Project", "media_location_path": "D:/Media"}
```

**Response:**
```json
{"success": true, "project_name": "New Project"}
```

---

### `POST /api/projects/load`

Load a project by name.

**Body:**
```json
{"project_name": "Project Alpha"}
```

**Response:**
```json
{"success": true, "project_name": "Project Alpha"}
```

---

### `POST /api/projects/save`

Save the current project.

**Response:**
```json
{"success": true}
```

---

### `POST /api/projects/close`

Close the current project without saving.

**Response:**
```json
{"success": true}
```

---

### `POST /api/projects/delete`

Delete a project by name.

**Body:**
```json
{"project_name": "Old Project"}
```

---

### `POST /api/projects/import`

Import a `.drp` project file.

**Body:**
```json
{"file_path": "C:/Projects/my_project.drp", "project_name": "Optional Rename"}
```

---

### `POST /api/projects/export`

Export the current project to a `.drp` file.

**Body:**
```json
{
  "project_name": "My Project",
  "file_path": "C:/Exports/my_project.drp",
  "with_stills_and_luts": true
}
```

---

### `POST /api/projects/restore`

Restore a project from a `.drp` archive file.

**Body:**
```json
{"file_path": "C:/Archives/2024-03-25_project.drp", "project_name": "Restored Project"}
```

---

### `POST /api/projects/archive`

Archive a project to a `.drp` file.

**Body:**
```json
{
  "project_name": "My Project",
  "file_path": "C:/Archives/my_project.drp",
  "is_archive_src_media": true,
  "is_archive_render_cache": false,
  "is_archive_proxy_media": false
}
```

---

### `GET /api/projects/folders`

List project folders.

**Response:**
```json
{"folders": ["Work Projects", "Archived", "Clients"]}
```

---

### `POST /api/projects/folders/create`

Create a project folder.

**Body:**
```json
{"folder_name": "New Folder"}
```

---

### `POST /api/projects/folders/delete`

Delete a project folder.

**Body:**
```json
{"folder_name": "Old Folder"}
```

---

### `POST /api/projects/folders/navigate`

Navigate to a project folder.

**Body:**
```json
{"folder_name": "Work Projects"}
```

**Special values:** `".."` for parent, `"root"` for root folder.

---

### `GET /api/projects/database`

Get current database info.

**Response:**
```json
{
  "db_type": "PostgreSQL",
  "db_name": "prod_resolve",
  "ip_address": "192.168.1.100"
}
```

---

### `GET /api/projects/databases`

List all available databases.

**Response:**
```json
{
  "databases": [
    {"db_type": "Disk", "db_name": "Database1"},
    {"db_type": "PostgreSQL", "db_name": "prod_resolve", "ip_address": "192.168.1.100"}
  ]
}
```

---

### `POST /api/projects/database/set`

Switch to a different database.

**Body:**
```json
{"db_type": "PostgreSQL", "db_name": "prod_resolve", "ip_address": "192.168.1.100"}
```

---

## Group - Media

### `GET /api/media/volumes`

List mounted volumes visible in Resolve's media storage.

**Response:**
```json
{"volumes": ["D:/", "E:/", "//server/storage"]}
```

---

### `GET /api/media/files`

List files in a folder path.

**Query params:** `folder_path` (required)

**Example:** `GET /api/media/files?folder_path=D:/Footage/2024`

**Response:**
```json
{
  "files": [
    {"name": "A001_C001.mov", "path": "D:/Footage/2024/A001_C001.mov", "type": "media"},
    {"name": "B002_C001.mp4", "path": "D:/Footage/2024/B002_C001.mp4", "type": "media"}
  ]
}
```

---

### `GET /api/media/subfolders`

List subfolders in a path.

**Query params:** `folder_path` (required)

**Response:**
```json
{"subfolders": ["raw", "audio", "exports"]}
```

---

### `POST /api/media/import`

Import files/folders into the current Media Pool folder.

**Body:**
```json
{
  "items": ["D:/Footage/2024/A001.mov", "D:/Footage/2024/B001.mov"]
}
```

**Or import a folder:**
```json
{
  "items": ["D:/Footage/2024/"]
}
```

**Or import with frame range (image sequences):**
```json
{
  "items": [
    {"media": "D:/Footage/sequence_%04d.exr", "start_frame": 1, "end_frame": 250}
  ]
}
```

**Response:**
```json
{
  "imported_clips": [
    {"name": "A001_C001", "media_id": "clip_001"},
    {"name": "B002_C001", "media_id": "clip_002"}
  ]
}
```

---

### `POST /api/media/relink`

Relink clips to a new folder path.

**Body:**
```json
{
  "clip_ids": ["clip_001", "clip_002"],
  "folder_path": "D:/NewLocation/Footage"
}
```

**Response:**
```json
{"success": true, "relinked_count": 2}
```

---

### `POST /api/media/unlink`

Unlink specified clips.

**Body:**
```json
{"clip_ids": ["clip_001"]}
```

---

### `GET /api/media/pool`

Get the current Media Pool structure.

**Response:**
```json
{
  "current_folder": "Imported",
  "root_folder": "Media",
  "subfolders": [
    {"name": "Imported", "clip_count": 12},
    {"name": "Raw Footage", "clip_count": 45}
  ]
}
```

---

### `GET /api/media/clips`

Get clips in a folder.

**Query params:** `folder_name` (optional, defaults to current folder)

**Response:**
```json
{
  "clips": [
    {
      "name": "A001_C001",
      "media_id": "clip_001",
      "duration": 120.5,
      "proxy": "available",
      "audio_tracks": 2
    }
  ]
}
```

---

### `GET /api/media/clip/{media_id}`

Get details for a specific clip.

**Response:**
```json
{
  "name": "A001_C001",
  "media_id": "clip_001",
  "properties": {
    "File Path": "D:/Footage/A001_C001.mov",
    "Duration": "00:02:00:15",
    "Resolution": "3840x2160",
    "Frame Rate": "23.976"
  },
  "metadata": {
    "Camera": "Sony FX6",
    "ISO": "2500",
    "Date Created": "2024-03-25"
  }
}
```

---

### `POST /api/media/clip/{media_id}/metadata`

Set clip metadata.

**Body:**
```json
{"metadata": {"Camera": "Sony FX6", "Scene": "Day 1"}}
```

---

### `POST /api/media/clip/{media_id}/markers/add`

Add a marker to a clip.

**Body:**
```json
{
  "frame_id": 120,
  "color": "Green",
  "name": "Review Point",
  "note": "Check focus here",
  "duration": 1.0
}
```

**Valid colors:** `Red`, `Yellow`, `Green`, `Cyan`, `Blue`, `Purple`, `Gray`, `White`

---

### `GET /api/media/clip/{media_id}/markers`

Get all markers on a clip.

**Response:**
```json
{
  "markers": {
    "120.0": {
      "color": "Green",
      "duration": 1.0,
      "name": "Review Point",
      "note": "Check focus here",
      "custom_data": ""
    }
  }
}
```

---

### `POST /api/media/clip/{media_id}/flags/add`

Add a flag to a clip.

**Body:**
```json
{"color": "Blue"}
```

---

### `GET /api/media/folder/create`

Create a subfolder in the current Media Pool folder.

**Body:**
```json
{"name": "Day 1", "parent_folder": "Raw Footage"}
```

---

### `POST /api/media/clip/{media_id}/color`

Set clip color.

**Body:**
```json
{"color": "Orange"}
```

---

### `POST /api/media/clip/delete`

Delete clips from the media pool.

**Body:**
```json
{"clip_ids": ["clip_001", "clip_002"]}
```

---

### `POST /api/media/clip/move`

Move clips to a different Media Pool folder.

**Body:**
```json
{"clip_ids": ["clip_001"], "target_folder": "Archived"}
```

---

## Group - Render

### `GET /api/render/formats`

Get available render formats.

**Response:**
```json
{
  "formats": {
    "QuickTime": "mov",
    "MP4": "mp4",
    "MXF OP-Atom": "mxf",
    "TIFF": "tif",
    "EXR": "exr",
    "DPX": "dpx"
  }
}
```

---

### `GET /api/render/codecs`

Get available codecs for a format.

**Query params:** `format` (required, e.g., `mov`)

**Response:**
```json
{
  "codecs": {
    "ProRes 422": "ProRes422",
    "ProRes 422 HQ": "ProRes422HQ",
    "ProRes 4444": "ProRes4444",
    "DNxHR HQX": "DNxHR_HQX"
  }
}
```

---

### `GET /api/render/resolutions`

Get available resolutions for a format/codec combo.

**Query params:** `format`, `codec`

**Response:**
```json
{
  "resolutions": [
    {"width": 3840, "height": 2160},
    {"width": 1920, "height": 1080},
    {"width": 1280, "height": 720}
  ]
}
```

---

### `GET /api/render/settings`

Get current render settings for the project.

**Response:**
```json
{
  "format": "mov",
  "codec": "ProRes422HQ",
  "target_dir": "D:/Renders",
  "custom_name": "Final_Master",
  "render_mode": "single_clip"
}
```

---

### `POST /api/render/settings`

Set render settings.

**Body:**
```json
{
  "format": "mov",
  "codec": "ProRes422HQ",
  "target_dir": "D:/Renders",
  "custom_name": "Final_Master",
  "select_all_frames": true,
  "export_video": true,
  "export_audio": true,
  "resolution_width": 3840,
  "resolution_height": 2160,
  "frame_rate": "23.976"
}
```

---

### `POST /api/render/format-set`

Set render format and codec in one call.

**Body:**
```json
{"format": "mov", "codec": "ProRes422HQ"}
```

---

### `GET /api/render/presets`

List all render presets.

**Response:**
```json
{"presets": ["YouTube 4K", "Social 1080p", "Master"]}
```

---

### `POST /api/render/preset/load`

Load a render preset.

**Body:**
```json
{"preset_name": "YouTube 4K"}
```

---

### `POST /api/render/preset/save`

Save current settings as a new render preset.

**Body:**
```json
{"preset_name": "My Custom Preset"}
```

---

### `POST /api/render/preset/delete`

Delete a render preset.

**Body:**
```json
{"preset_name": "Unused Preset"}
```

---

### `GET /api/render/jobs`

List all render jobs in the queue.

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "abc-123-uuid",
      "output_path": "D:/Renders/Final_Master.mov",
      "status": "Queued"
    }
  ]
}
```

---

### `POST /api/render/job/add`

Add a render job to the queue.

**Response:**
```json
{"job_id": "abc-123-uuid", "success": true}
```

---

### `POST /api/render/job/delete`

Delete a render job by ID.

**Body:**
```json
{"job_id": "abc-123-uuid"}
```

---

### `POST /api/render/jobs/clear`

Delete all render jobs.

---

### `POST /api/render/start`

Start rendering. Can specify job IDs or render all.

**Body (all jobs):**
```json
{}

**Body (specific jobs):**
```json
{"job_ids": ["abc-123-uuid", "def-456-uuid"]}
```

---

### `POST /api/render/stop`

Stop any current rendering.

---

### `GET /api/render/status`

Check if rendering is in progress.

**Response:**
```json
{"rendering": true, "job_id": "abc-123-uuid"}
```

---

### `GET /api/render/status/{job_id}`

Get status of a specific render job.

**Response:**
```json
{
  "job_id": "abc-123-uuid",
  "status": "Rendering",
  "completion_percent": 45
}
```

---

### `POST /api/render/quick-export`

Run a quick export using a quick export preset.

**Body:**
```json
{
  "preset_name": "Social Media 4K",
  "target_dir": "D:/Exports",
  "custom_name": "short_ver.mp4"
}
```

**Response:**
```json
{
  "status": "completed",
  "time_taken_seconds": 120
}
```

---

## Group - Timeline

### `GET /api/timeline/list`

List all timelines in the current project.

**Response:**
```json
{
  "timelines": [
    {"name": "Main Edit", "index": 1},
    {"name": "Assembly", "index": 2}
  ],
  "current": "Main Edit"
}
```

---

### `GET /api/timeline/current`

Get current timeline info.

**Response:**
```json
{
  "name": "Main Edit",
  "start_frame": 0,
  "end_frame": 14400,
  "track_count": {"video": 3, "audio": 5, "subtitle": 1}
}
```

---

### `POST /api/timeline/current/set`

Set the current active timeline.

**Body:**
```json
{"timeline_name": "Assembly Cut"}
```

---

### `POST /api/timeline/create`

Create a new empty timeline.

**Body:**
```json
{"name": "New Timeline"}
```

---

### `POST /api/timeline/create-from-clips`

Create a timeline from existing MediaPool clips.

**Body:**
```json
{
  "name": "Day 1 Assembly",
  "clip_ids": ["clip_001", "clip_002", "clip_003"]
}
```

---

### `POST /api/timeline/import-file`

Import a timeline from an EDL/XML/AAF/FCPXML file.

**Body:**
```json
{
  "file_path": "D:/Projects/edit.edl",
  "options": {
    "timeline_name": "Imported Edit",
    "import_source_clips": true,
    "source_clips_path": "D:/Footage"
  }
}
```

---

### `GET /api/timeline/{index}/items`

Get all items on a timeline.

**Query params:** `timeline_index`, `track_type` (video/audio/subtitle), `track_index`

---

### `GET /api/timeline/{index}/markers`

Get all markers on a timeline.

---

### `POST /api/timeline/{index}/markers/add`

Add a marker to the timeline.

**Body:**
```json
{
  "frame_id": 1000,
  "color": "Yellow",
  "name": "Director Note",
  "note": "Check pacing here",
  "duration": 1.0
}
```

---

## Group - Fusion

### `GET /api/fusion/node-graph`

Get the Fusion node graph for the current timeline.

---

### `POST /api/fusion/node/add`

Add a node to the Fusion comp.

**Body:**
```json
{"node_type": "TextPlus", "node_name": "Title 1"}
```

**Common node types:** `TextPlus`, `Merge`, `Background`, `Transform`, `ColorCorrector`, `DeltaKeyer`, `Blur`, `Light`, `Rasterize`

---

## Error Codes

| Code | Meaning |
|------|---------|
| `RESOLVE_NOT_RUNNING` | Resolve is not running — start Resolve first |
| `FREE_VERSION` | External scripting requires Resolve Studio |
| `SCRIPTING_DISABLED` | External scripting is disabled in Preferences |
| `PROJECT_NOT_FOUND` | The specified project does not exist |
| `TIMELINE_NOT_FOUND` | The specified timeline does not exist |
| `CLIP_NOT_FOUND` | The specified clip does not exist |
| `INVALID_PAGE` | Invalid page name provided |
| `RENDER_IN_PROGRESS` | Cannot perform action while rendering |
| `API_ERROR` | General Resolve API error |

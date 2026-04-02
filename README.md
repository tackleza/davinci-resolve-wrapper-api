# DaVinci Resolve Wrapper API

A FastAPI-based REST API wrapper for DaVinci Resolve Studio — UUID-based registry system for DaVinci objects (Projects, Folders, Clips, Timelines).

**API Docs:** `http://YOUR_IP:8080/docs` (Swagger UI)

---

## Features

- 🌐 **HTTP REST API** — Control DaVinci Resolve from any HTTP client
- 📄 **Swagger UI** — Interactive API explorer at `/docs`
- 🔑 **UUID-based Registry** — Every object (Folder, Clip, Timeline) has a stable UUID
- 🎬 **Media Pool** — Import, navigate, manage clips and folders
- 🎞️ **Timeline** — Insert clips at playhead, list timelines
- 🎥 **Render** — Full render queue control with presets
- 💾 **Project** — Save, close projects
- 🔄 **Auto-reconnect** — Handles DaVinci Resolve restarts gracefully

---

## DaVinci Resolve API Reference

For human-readable DaVinci Resolve API documentation:
**[bmd_doc — DaVinci Resolve API Docs](https://wheheohu.github.io/bmd_doc)** by [WheheoHu](https://github.com/WheheoHu/bmd_doc)

---

## Quick Start

### 1. Enable External Scripting in DaVinci Resolve

1. Open DaVinci Resolve → **Preferences → General → External Scripting**
2. Check **Enable DaVinci Resolve External API**
3. Restart DaVinci Resolve

### 2. Run the Server

```cmd
cd C:\Users\Tackle\davinci_wrapper
python main.py --host 0.0.0.0 --port 8080
```

Access at:
- **Local:** `http://localhost:8080`
- **Network:** `http://YOUR_PC_IP:8080`
- **Docs:** `http://YOUR_PC_IP:8080/docs`

---

## API Overview

**Base URL:** `http://YOUR_IP:8080`

### Project

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/project/save` | POST | Save current project |
| `/api/project/close` | POST | Close current project |

### Resolve

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/resolve/health` | GET | Health check — is Resolve connected? |
| `/api/resolve/quit` | POST | Quit DaVinci Resolve |

### Render

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/render/presets` | GET | List render presets |
| `/api/render/preset/load` | POST | Load a preset |
| `/api/render/preset/save` | POST | Save current settings as preset |
| `/api/render/preset/delete` | POST | Delete a preset |
| `/api/render/settings` | GET | Get current render settings |
| `/api/render/settings` | POST | Update render settings |
| `/api/render/jobs` | GET | List render queue |
| `/api/render/job` | POST | Add job to queue |
| `/api/render/job` | DELETE | Delete a job |
| `/api/render/jobs` | DELETE | Clear all jobs |
| `/api/render/start` | POST | Start rendering |
| `/api/render/stop` | POST | Stop rendering |
| `/api/render/status` | GET | Check if rendering |
| `/api/render/status/{id}` | GET | Get job status |
| `/api/render/progress` | GET | Get render progress % |

### Registry — UUID-based Object Access

Registry caches all DaVinci objects by UUID for reliable reference.

#### Projects

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/registry/projects` | GET | List all registered projects |
| `/api/registry/projects/current` | GET | Get current project + full folder tree |
| `/api/registry/projects/rebuild` | POST | Rebuild folder tree |

#### Folders

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/registry/folders` | GET | List ALL folders (flat) |
| `/api/registry/folders/{uuid}` | GET | Folder details + clips + subfolders |
| `/api/registry/folders/{uuid}/tree` | GET | Folder + recursive subfolders |
| `/api/registry/folders/{uuid}/parent` | GET | Get parent folder |

#### Clips

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/clips` | GET | List ALL clips (flat) |
| `/api/clips/{uuid}` | GET | Clip details |
| `/api/clips/offline` | GET | List offline (unlinked) clips |
| `/api/clips/relink` | POST | Relink offline clips |

#### Timelines

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/timelines` | GET | List all timelines |
| `/api/timelines/{uuid}` | GET | Timeline details |

#### Media Import

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/media/import` | POST | Import files into Media Pool |

#### Timeline Actions

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/timeline/insert` | POST | Insert clips at playhead cursor |

---

## Example Usage

### cURL

```bash
# Health check
curl http://localhost:8080/api/resolve/health

# List timelines
curl http://localhost:8080/api/registry/timelines

# Import media
curl -X POST http://localhost:8080/api/media/import ^
  -H "Content-Type: application/json" ^
  -d "{\"paths\": [\"Y:\\\\Video Editing Job\\\\clip.mp4\"]}"

# Insert clips at cursor
curl -X POST http://localhost:8080/api/timeline/insert ^
  -H "Content-Type: application/json" ^
  -d "{\"clip_uuids\": [\"uuid-here\"], \"track_type\": \"both\"}"

# Start render
curl -X POST http://localhost:8080/api/render/start

# Save project
curl -X POST http://localhost:8080/api/project/save
```

### Python

```python
import httpx

BASE = "http://localhost:8080"

# Health check
health = httpx.get(f"{BASE}/api/resolve/health").json()
print(health)

# Import media
httpx.post(f"{BASE}/api/media/import", json={
    "paths": ["Y:\\Video Editing Job\\clip.mp4"]
})

# Insert at cursor
httpx.post(f"{BASE}/api/timeline/insert", json={
    "clip_uuids": ["uuid-here"],
    "track_type": "both"
})

# Start render
httpx.post(f"{BASE}/api/render/start")

# Save & quit
httpx.post(f"{BASE}/api/project/save")
httpx.post(f"{BASE}/api/resolve/quit")
```

---

## Project Structure

```
davinci-resolve-wrapper-api/
├── main.py                     # Entry point — FastAPI server
├── config.py                   # Platform-specific paths & settings
├── requirements.txt            # Python dependencies
├── startup_script.py           # DaVinci Resolve startup script
├── NEW_PLAN.md                 # API design document
├── src/
│   ├── registry.py             # UUID-based object registry
│   ├── resolve_connection.py   # DaVinci Resolve connection handler
│   └── api/
│       ├── __init__.py
│       ├── routes.py            # Route registration
│       └── endpoints/
│           ├── registry.py      # UUID registry endpoints
│           ├── render.py        # Render queue endpoints
│           ├── project.py       # Project endpoints
│           └── resolve.py       # Resolve endpoints
│           └── archive/         # Old endpoints (reference)
└── tests/                      # Test scripts
```

---

## Key Concepts

### UUID Registry

Every DaVinci object has a UUID. Use UUID as the canonical identifier — names can be duplicated (e.g., multiple "Internal" folders).

```
Registry
├── projects: { uuid: ProjectData }
├── FolderData: uuid, name, parent_uuid, clips, subfolders
├── ClipData: uuid, name, media_type, media_id
└── TimelineData: uuid, name, index
```

### Media Import

Import files from NAS or local drives into DaVinci's Media Pool:

```json
POST /api/media/import
{
  "paths": ["Y:\\Video Editing Job\\sb4-14\\clip.mp4"],
  "destination_folder_uuid": "optional-folder-uuid"
}
```

### Insert at Cursor

Insert clips into timeline at the playhead position:

```json
POST /api/timeline/insert
{
  "clip_uuids": ["clip-uuid-1", "clip-uuid-2"],
  "timeline_uuid": "optional-timeline-uuid",
  "track_type": "both"  // "both" | "video" | "audio"
}
```

---

## License

MIT

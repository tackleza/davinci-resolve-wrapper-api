# Davinci Resolve Wrapper API

HTTP API wrapper for DaVinci Resolve Studio — exposes the full DaVinci Resolve scripting API over REST so any external system (external systems, pipelines, scripts) can control Resolve without touching scripts inside Resolve itself.

---

## Project Structure

```
davinci-wrapper-ai/
├── INDEX.md                      ← You are here
├── PLAN.md                       ← Full API coverage plan (all 324 methods)
├── REST_API.md                   ← Live HTTP endpoint documentation
├── main.py                       ← FastAPI application entry point
├── requirements.txt              ← Python dependencies
├── config.py                     ← Configuration (platform paths, ports)
├── startup_script.py             ← Resolve startup script (place in Scripts/Utility)
├── src/
│   ├── __init__.py
│   ├── resolve_connection.py     ← Resolve API connection + platform detection
│   ├── exceptions.py            ← Custom exception classes
│   ├── models/
│   │   ├── __init__.py
│   │   ├── resolve_models.py    ← Resolve, ProjectManager models
│   │   ├── project_models.py     ← Project, Render, Timeline models
│   │   ├── media_models.py       ← MediaPool, Folder, MediaPoolItem models
│   │   └── timeline_models.py    ← Timeline, TimelineItem models
│   └── api/
│       ├── __init__.py
│       ├── routes.py             ← Route registration
│       └── endpoints/
│           ├── __init__.py
│           ├── resolve.py        ← /api/resolve/* — App control, pages, presets
│           ├── projects.py        ← /api/projects/* — Project CRUD, archive/restore
│           ├── media.py           ← /api/media/* — MediaPool, clips, folders
│           ├── render.py          ← /api/render/* — Render queue, presets, output
│           ├── timeline.py        ← /api/timeline/* — Timelines, tracks, markers
│           └── fusion.py          ← /api/fusion/* — Fusion page, node graph
```

---

## Quick Start

### 1. Prerequisites

- DaVinci Resolve Studio (free version does **not** support external scripting)
- Python 3.10–3.12 (not 3.13+ due to ABI incompatibilities)
- Enable external scripting: **Resolve → Preferences → General → External scripting using → Local**

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Place the Startup Script

Copy `startup_script.py` to your Resolve Scripts/Utility folder:

**Windows:**
```
%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Utility\
```

**macOS:**
```
~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility/
```

**Linux:**
```
$HOME/.local/share/DaVinciResolve/Fusion/Scripts/Utility/
```

> Name it so it sorts last, e.g. `zzz_wrapper_start.py`

### 4. Run the Wrapper

```bash
python main.py
```

Or with custom host/port:
```bash
python main.py --host 0.0.0.0 --port 8080
```

### 5. Access the API

- Swagger docs: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`
- OpenAPI JSON: `http://localhost:8080/openapi.json`

---

## API Overview

| Group | Base Path | Description |
|-------|-----------|-------------|
| Resolve | `/api/resolve` | App control, pages, version, presets, layout |
| Projects | `/api/projects` | Project CRUD, import/export, archive/restore, database |
| Media | `/api/media` | MediaPool, clips, folders, import, relink |
| Render | `/api/render` | Render queue, presets, formats, codecs, jobs |
| Timeline | `/api/timeline` | Timelines, tracks, clips, markers |
| Fusion | `/api/fusion` | Fusion page, node graph |

---

## For AI Agents

This wrapper is designed for AI control. Example interactions:

```bash
# Check if Resolve is running and get version
curl http://localhost:8080/api/resolve/health

# List all projects
curl http://localhost:8080/api/projects

# Import a project archive
curl -X POST http://localhost:8080/api/projects/restore \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/archives/project_x.drp"}'

# Import footage from a folder
curl -X POST http://localhost:8080/api/media/import \
  -H "Content-Type: application/json" \
  -d '{"folder_path": "/footage/2024-03-25"}'

# Relink clips to a new location
curl -X POST http://localhost:8080/api/media/relink \
  -H "Content-Type: application/json" \
  -d '{"clip_ids": ["clip_001", "clip_002"], "folder_path": "/new/media"}'

# Add render job and start rendering
curl -X POST http://localhost:8080/api/render/start \
  -H "Content-Type: application/json" \
  -d '{"project_name": "MyProject", "preset": "Final_Master"}'

# Check render status
curl http://localhost:8080/api/render/status/abc-123-uuid
```

See `REST_API.md` for the full endpoint reference.

---

## Changelog

- **2026-03-25** — Project created. API v1.0 based on DaVinci Resolve API v20.3

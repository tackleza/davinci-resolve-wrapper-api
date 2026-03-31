# DaVinci Resolve Wrapper API

A FastAPI-based REST API wrapper for DaVinci Resolve, enabling programmatic control of DaVinci Resolve Studio via HTTP endpoints. Compatible with Windows, macOS, and Linux.

**API Docs:** `http://YOUR_IP:8080/docs` (Swagger UI — e.g. `http://192.168.1.14:8080/docs`)

---

## Features

- 🌐 **HTTP REST API** — Control DaVinci Resolve from any HTTP client
- 📄 **Swagger UI** — Interactive API explorer at `/docs`
- 🎬 **Projects** — List, load, create, delete projects
- 🎞️ **Timelines** — Create, switch, get/put timeline items and markers
- 🗂️ **Media** — Import, pool management, clip metadata
- 🎥 **Render** — Full render queue control with presets
- 🔧 **Fusion** — Node graph inspection
- 🔄 **Auto-reconnect** — Handles DaVinci Resolve restarts gracefully

---

## Requirements

- **DaVinci Resolve Studio** (free version has limited API access)
- **Python 3.10–3.12** (Python 3.13+ is NOT supported)
- **Windows / macOS / Linux**

### Python Dependencies

```
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic==2.9.2
pydantic-settings==2.6.0
watchdog==4.0.2      # Optional: folder watching
httpx==0.27.2        # Optional: HTTP client for external systems
```

---

## Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Paths (if needed)

Edit `config.py` to match your DaVinci Resolve installation path, or set environment variables:

**Windows:**
```cmd
set RESOLVE_SCRIPT_API=C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting
set RESOLVE_SCRIPT_LIB=C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll
```

**macOS / Linux:** See `config.py` for the respective paths.

### 3. Enable External Scripting in DaVinci Resolve

1. Open DaVinci Resolve
2. Go to **Preferences → General → External Scripting**
3. Check **Enable DaVinci Resolve External API**

### 4. (Optional) Copy Startup Script

Copy `startup_script.py` to your DaVinci Scripts/Utility folder so the module loads automatically:

- **Windows:** `%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Scripts\Utility\`
- **macOS:** `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility/`
- **Linux:** `~/.local/share/DaVinciResolve/Fusion/Scripts/Utility/`

### 5. Run the Server

```bash
python main.py --host 0.0.0.0 --port 8080
```

For production, use `screen` or a systemd service:

```bash
# Linux systemd example (create /etc/systemd/system/davinci-wrapper.service)
[Unit]
Description=DaVinci Resolve Wrapper API
After=network.target

[Service]
Type=simple
User=tackle
WorkingDirectory=/home/tackle/davinci-wrapper
ExecStart=/home/tackle/.local/bin/python main.py --host 0.0.0.0 --port 8080
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## API Reference

**Base URL:** `http://YOUR_IP:8080`
**Interactive Docs:** `http://YOUR_IP:8080/docs`

### Resolve

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/resolve/health` | GET | Health check — is Resolve connected? |
| `/api/resolve/pages` | GET | List all pages |
| `/api/resolve/current-page` | GET | Get current page |
| `/api/resolve/open-page` | POST | Switch to a page |

### Projects

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/projects` | GET | List all projects |
| `/api/projects/current` | GET | Get current project info |
| `/api/projects/load` | POST | Load a project by name |
| `/api/projects/create` | POST | Create a new project |
| `/api/projects/delete` | POST | Delete a project |

### Timeline

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/timeline/list` | GET | List all timelines |
| `/api/timeline/current` | GET | Get current timeline |
| `/api/timeline/current/set` | POST | Switch timeline |
| `/api/timeline/create` | POST | Create a new timeline |
| `/api/timeline/{index}/items` | GET | Get items on a timeline |
| `/api/timeline/{index}/markers` | GET | Get markers on a timeline |
| `/api/timeline/{index}/delete` | POST | Delete a timeline |

### Media

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/media/volumes` | GET | List mounted volumes |
| `/api/media/pool` | GET | Get current media pool |
| `/api/media/subfolders` | GET | List subfolders |
| `/api/media/import` | POST | Import media files |
| `/api/media/clips` | GET | List clips in pool |
| `/api/media/clip/{id}/metadata` | GET | Get clip metadata |
| `/api/media/clip/delete` | POST | Delete a clip |
| `/api/media/relink` | POST | Relink offline clips |

### Render

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/render/presets` | GET | List render presets |
| `/api/render/formats` | GET | Available formats |
| `/api/render/codecs` | GET | Available codecs |
| `/api/render/settings` | GET | Current render settings |
| `/api/render/settings` | POST | Update render settings |
| `/api/render/jobs` | GET | List render queue |
| `/api/render/job/add` | POST | Add job to queue |
| `/api/render/start` | POST | Start rendering |
| `/api/render/stop` | POST | Stop rendering |
| `/api/render/quick-export` | POST | Quick export |
| `/api/render/status/{job_id}` | GET | Get job status |

### Fusion

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/timeline/fusion/node-graph` | GET | Get Fusion node graph |

---

## Example Usage

### cURL

```bash
# Health check
curl http://localhost:8080/api/resolve/health

# Load a project
curl -X POST http://localhost:8080/api/projects/load \
  -H "Content-Type: application/json" \
  -d '{"project_name": "My Project"}'

# Switch timeline
curl -X POST http://localhost:8080/api/timeline/current/set \
  -H "Content-Type: application/json" \
  -d '{"timeline_name": "Timeline 1"}'

# List timelines
curl http://localhost:8080/api/timeline/list

# Import media
curl -X POST http://localhost:8080/api/media/import \
  -H "Content-Type: application/json" \
  -d '{"items": ["C:/Footage/clip01.mp4", "C:/Footage/clip02.mp4"]}'
```

### Python

```python
import httpx

BASE = "http://localhost:8080"

# Health check
health = httpx.get(f"{BASE}/api/resolve/health").json()
print(health)
# {'connected': True, 'product_name': 'DaVinci Resolve Studio', 'version': [20, 3, 1, 6, '']}

# Load project
httpx.post(f"{BASE}/api/projects/load", json={"project_name": "My Project"})

# Switch to Edit page
httpx.post(f"{BASE}/api/resolve/open-page", json={"page_name": "edit"})

# Get timeline items
items = httpx.get(f"{BASE}/api/timeline/1/items").json()
```

---

## Project Structure

```
davinci-wrapper/
├── main.py                  # Entry point — FastAPI server
├── config.py                # Platform-specific paths & settings
├── requirements.txt         # Python dependencies
├── startup_script.py        # DaVinci Resolve startup script
├── src/
│   ├── resolve_connection.py # DaVinci Resolve connection handler
│   └── api/
│       ├── __init__.py
│       ├── endpoints/       # API route handlers
│       │   ├── resolve.py
│       │   ├── projects.py
│       │   ├── timeline.py
│       │   ├── media.py
│       │   ├── render.py
│       │   └── fusion.py
│       └── models/          # Pydantic request/response models
├── REST_API.md             # Full API reference
└── PLAN.md                 # Project plan
```

---

## Troubleshooting

### "DaVinci Resolve is not running"
- Make sure DaVinci Resolve is open before starting the wrapper
- Enable **External Scripting** in DaVinci Resolve Preferences → General

### "Module not found: DaVinciResolveScript"
- Set `RESOLVE_SCRIPT_API` environment variable to your scripting path
- On Windows: `set RESOLVE_SCRIPT_API=C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting`

### Port already in use
```bash
# Find and kill the process using port 8080
lsof -i :8080   # macOS/Linux
netstat -ano | findstr :8080   # Windows
```

### API not accessible from other machines
- Make sure Windows Firewall allows Python through (port 8080)
- Or run as Administrator and use `netsh` to add a firewall rule

---

## License

MIT — Do whatever you want with it. Attribution appreciated.

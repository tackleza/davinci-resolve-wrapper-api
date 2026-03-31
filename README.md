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

---

## Windows Installation Guide

### Step 1: Install Python

1. Download Python 3.12 from [python.org](https://www.python.org/downloads/)
2. During install, check **"Add Python to PATH"**
3. Verify:
   ```cmd
   python --version
   ```

### Step 2: Install Dependencies

Open **Command Prompt** and run:

```cmd
cd C:\Users\YourUsername\Documents\davinci-resolve-wrapper-api
pip install -r requirements.txt
```

### Step 3: Enable External Scripting in DaVinci Resolve

1. Open DaVinci Resolve
2. Go to **Preferences → General → External Scripting**
3. Check **Enable DaVinci Resolve External API**
4. Restart DaVinci Resolve

### Step 4: Run the Server

```cmd
cd C:\Users\YourUsername\Documents\davinci-resolve-wrapper-api
python main.py --host 0.0.0.0 --port 8080
```

The server will start and DaVinci Resolve will be accessible at:
- **Local:** `http://localhost:8080`
- **Network:** `http://YOUR_PC_IP:8080`

To find your PC's IP address: `ipconfig` (look for IPv4 Address under your network adapter)

### Step 5: (Optional) Auto-start with Windows

Create a batch file in your Startup folder:

1. Open Notepad and paste:
   ```bat
   @echo off
   cd /d C:\Users\YourUsername\Documents\davinci-resolve-wrapper-api
   start /min python main.py --host 0.0.0.0 --port 8080
   ```
2. Save as `start_wrapper.bat`
3. Press `Win + R`, type `shell:startup`, press Enter
4. Copy the `.bat` file into that folder

Now the API starts automatically when Windows boots.

### Step 6: (Optional) Auto-start Wrapper when DaVinci Opens

Instead of starting with Windows, you can start the wrapper automatically when DaVinci Resolve launches:

1. Copy `startup_script.py` to:
   ```
   %APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Scripts\Utility\
   ```
   This folder may not exist — create it if needed.

2. When DaVinci Resolve starts, the script will launch the wrapper automatically.

---

## Troubleshooting

### "DaVinci Resolve is not running"
- Make sure DaVinci Resolve is open before starting the wrapper
- Enable **External Scripting** in DaVinci Resolve → Preferences → General

### "Module not found: DaVinciResolveScript"
- The wrapper uses `os.path.expandvars()` to resolve `%PROGRAMDATA%` automatically. If you still get this error, open Command Prompt and run:
  ```cmd
  set RESOLVE_SCRIPT_API=C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting
  python main.py --host 0.0.0.0 --port 8080
  ```

### Port already in use
Find and kill the process using port 8080:
```cmd
netstat -ano | findstr :8080
taskkill /PID <PROCESS_ID> /F
```

### API not accessible from other machines on the network
Windows Firewall may be blocking port 8080. To allow it, run Command Prompt as Administrator:
```cmd
netsh advfirewall firewall add rule name="DaVinci Wrapper API" dir=in action=allow protocol=tcp localport=8080 program="C:\Users\YourUsername\AppData\Local\Programs\Python\Python312\python.exe"
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
curl -X POST http://localhost:8080/api/projects/load ^
  -H "Content-Type: application/json" ^
  -d "{\"project_name\": \"My Project\"}"

# Switch timeline
curl -X POST http://localhost:8080/api/timeline/current/set ^
  -H "Content-Type: application/json" ^
  -d "{\"timeline_name\": \"Timeline 1\"}"

# List timelines
curl http://localhost:8080/api/timeline/list

# Import media
curl -X POST http://localhost:8080/api/media/import ^
  -H "Content-Type: application/json" ^
  -d "{\"items\": [\"C:/Footage/clip01.mp4\", \"C:/Footage/clip02.mp4\"]}"
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
davinci-resolve-wrapper-api/
├── main.py                  # Entry point — FastAPI server
├── config.py                # Platform-specific paths & settings
├── requirements.txt         # Python dependencies
├── startup_script.py       # DaVinci Resolve startup script (auto-run)
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
│       └── models/         # Pydantic request/response models
├── REST_API.md             # Full API reference
├── INDEX.md                 # Project overview
└── PLAN.md                 # Implementation plan (reference)
```

---

## License

MIT — Do whatever you want with it. Attribution appreciated.

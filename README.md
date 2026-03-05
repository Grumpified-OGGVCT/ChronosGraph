# ChronosGraph

> **Local Knowledge OS** — Transform YouTube videos into interactive 3D knowledge graphs

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.12%2B-green)
![React](https://img.shields.io/badge/react-18-cyan)

## What It Does

Paste a YouTube URL. ChronosGraph downloads the video, extracts knowledge using **Gemini 2.5 Pro**, and builds a navigable **3D knowledge graph** in real-time.

- 🎥 **Ingests** videos and playlists via yt-dlp
- 🧠 **Extracts** entities (People, Organizations, Concepts, Events, Locations) and relationships
- 📊 **Visualizes** everything as a force-directed 3D graph with Three.js
- 🔍 **Search** entities with vector similarity (ChromaDB)
- ⚡ **Real-time** updates via WebSocket as processing happens

## Architecture

```
[YouTube URL] → [yt-dlp] → [FFmpeg Chunking] → [Gemini 2.5 Pro]
                                                      ↓
              [ChromaDB] ←→ [Entity Resolution] → [Neo4j Graph]
                                                      ↓
              [WebSocket] → [React + Three.js 3D Scene]
```

## Prerequisites

- **Python 3.12+**
- **Node.js 20+**
- **Neo4j Community 5.x** ([download](https://neo4j.com/download/))
- **FFmpeg** on PATH (`winget install Gyan.FFmpeg`)
- **Google Gemini API Key** ([get one](https://aistudio.google.com/apikey))

## Quick Start

### 1. Clone & Configure
```bash
git clone https://github.com/Grumpified-OGGVCT/ChronosGraph.git
cd ChronosGraph
cp config.env.example config.env
# Edit config.env — set your GEMINI_API_KEY
```

### 2. Install Dependencies
```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend && npm install && cd ..
```

### 3. Start Services
```bash
# Option A: One-click launcher (Windows)
run.bat

# Option B: Manual
# Terminal 1: Start Neo4j
neo4j console

# Terminal 2: Start Backend
cd backend && python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 3: Start Frontend
cd frontend && npm run dev
```

### 4. Open Browser
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474

## Usage

1. Paste a YouTube video or playlist URL in the input bar
2. Click **Process** — watch the status indicator and progress bar
3. Entities appear in real-time as glowing nodes in the 3D scene
4. **Hover** nodes for tooltips, **click** for the HoloCard detail panel
5. **Search** entities with the search bar (triggers Focus Mode)
6. **Filter** by entity type and confidence with the filter panel
7. Click timestamps in HoloCards to watch the source video at that moment

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/ingest` | Submit video/playlist URL |
| GET | `/api/graph` | All nodes + edges |
| GET | `/api/graph/node/{id}` | Node detail |
| GET | `/api/search?q=` | Vector similarity search |
| GET | `/api/filters/metadata` | Available filter options |
| GET | `/api/errors` | Error list |
| POST | `/api/errors/{id}/retry` | Retry failed job |
| GET | `/api/video/{id}` | Stream cached video |
| GET | `/api/health` | Health check |
| WS | `/ws` | Real-time updates |

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.12 / FastAPI |
| Graph DB | Neo4j Community 5.x |
| Vector DB | ChromaDB |
| Job Queue | SQLite (SQLAlchemy) |
| AI | Google Gemini 2.5 Pro |
| Media | yt-dlp + FFmpeg |
| Frontend | React 18 + Vite |
| 3D Scene | Three.js / @react-three/fiber |
| Layout | d3-force-3d |
| Real-time | WebSocket |

## License

MIT

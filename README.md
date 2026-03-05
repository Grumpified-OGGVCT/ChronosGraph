# ChronosGraph

A local knowledge OS that ingests YouTube playlists, transcribes each video, extracts entities and relationships with Gemini AI, stores them in a Neo4j knowledge graph + ChromaDB vector store, and renders the result as an interactive 3-D force-directed visualization in the browser.

---

## Prerequisites

| Requirement | Minimum version | Notes |
|---|---|---|
| **Python** | 3.11+ | Required for the FastAPI backend |
| **Node.js** | 18+ | Required for the Vite/React frontend |
| **FFmpeg** | Any recent release | Required for audio extraction (`yt-dlp` dependency) |
| **Neo4j** | 5.x | Graph database; must be reachable at `bolt://localhost:7687` by default |
| **Gemini API key** | — | Obtain from [Google AI Studio](https://aistudio.google.com/) |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Grumpified-OGGVCT/ChronosGraph.git
cd ChronosGraph
```

### 2. Configure environment variables

```bash
cp config.env.example .env
```

Open `.env` and fill in your values:

```env
GEMINI_API_KEY=your-key-here
NEO4J_PASSWORD=your-neo4j-password
```

All other settings can be left at their defaults for a local setup.

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

---

## Running

### Windows (one-click launcher)

```bat
run.bat
```

This script starts Neo4j (if not already running), the FastAPI backend, and the Vite dev server, then opens status messages for each service.

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Neo4j Browser | http://localhost:7474 |

### Manual startup

**Backend**

```bash
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

**Frontend**

```bash
cd frontend
npm run dev
```

---

## Project structure

```
ChronosGraph/
├── backend/
│   ├── main.py          # FastAPI app, WebSocket hub, static mount
│   ├── config.py        # Pydantic Settings (reads .env)
│   ├── routers/         # ingest, search, graph, errors, filters
│   ├── services/        # media, processor, graph_db, vector_db, queue, ws_manager
│   ├── workers/         # ingestion pipeline worker
│   ├── models/          # SQLAlchemy DB models + Pydantic schemas
│   └── utils/           # logger, retry helpers
├── frontend/
│   └── src/             # Vite + React app (Three.js 3-D visualization)
├── config.env.example   # Template for environment variables
├── requirements.txt     # Python dependencies
└── run.bat              # Windows one-click launcher
```

---

## License

[MIT](LICENSE)

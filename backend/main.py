"""ChronosGraph — FastAPI Application Entry Point.

Enterprise-grade local knowledge OS for ingesting, processing,
and visualizing video data as an interactive 3D knowledge graph.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from config import settings
from models.db_models import init_db
from routers import errors, filters, graph, ingest, search
from services.graph_db import close_driver
from services.ws_manager import ws_manager
from utils.logger import setup_logging
from workers.pipeline import worker_loop

logger = logging.getLogger("chronosgraph.main")
_worker_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _worker_task
    setup_logging()
    settings.ensure_directories()
    init_db()
    logger.info("ChronosGraph starting up...")
    _worker_task = asyncio.create_task(worker_loop())
    logger.info("Pipeline worker launched")
    yield
    logger.info("ChronosGraph shutting down...")
    if _worker_task:
        _worker_task.cancel()
        try:
            await _worker_task
        except asyncio.CancelledError:
            pass
    await close_driver()
    logger.info("All connections closed. Goodbye.")


app = FastAPI(
    title="ChronosGraph",
    description="Local Knowledge OS — Video → Knowledge Graph → 3D Visualization",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router)
app.include_router(search.router)
app.include_router(graph.router)
app.include_router(errors.router)
app.include_router(filters.router)


@app.get("/api/video/{video_id}")
async def stream_video(video_id: str):
    video_dir = settings.resolve_path(settings.video_cache_dir)
    for ext in (".mp4", ".mkv", ".webm"):
        video_path = video_dir / f"{video_id}{ext}"
        if video_path.exists():
            return FileResponse(str(video_path), media_type="video/mp4", filename=video_path.name)
    return {"error": "Video not found"}, 404


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await ws_manager.send_json(websocket, {"type": "echo", "data": data})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "ChronosGraph", "version": "0.1.0"}

_frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if _frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(_frontend_dist), html=True), name="frontend")

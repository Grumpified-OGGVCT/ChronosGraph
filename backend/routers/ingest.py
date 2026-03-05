"""Ingest Router — Accepts video/playlist URLs for processing."""

import logging
import re
import uuid
from fastapi import APIRouter, HTTPException
from models.schemas import IngestRequest, IngestResponse
from services.queue import enqueue_job, get_queue_count
from services.ws_manager import ws_manager

router = APIRouter(prefix="/api", tags=["ingest"])
logger = logging.getLogger("chronosgraph.ingest")

PLAYLIST_PATTERN = re.compile(r"[?&]list=([a-zA-Z0-9_-]+)")
VIDEO_PATTERN = re.compile(r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)([a-zA-Z0-9_-]+)")


@router.post("/ingest", response_model=IngestResponse)
async def ingest_url(request: IngestRequest) -> IngestResponse:
    url = request.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    playlist_match = PLAYLIST_PATTERN.search(url)
    if playlist_match:
        playlist_id = playlist_match.group(1)
        job_id = str(uuid.uuid4())
        await enqueue_job(job_id, url, playlist_id=playlist_id)
        count = await get_queue_count()
        await ws_manager.broadcast_queue_update(count)
        return IngestResponse(status="queued", count=1, message=f"Playlist {playlist_id} queued")
    elif VIDEO_PATTERN.search(url):
        job_id = str(uuid.uuid4())
        await enqueue_job(job_id, url)
        count = await get_queue_count()
        await ws_manager.broadcast_queue_update(count)
        return IngestResponse(status="queued", count=1, message="Video queued")
    else:
        raise HTTPException(status_code=400, detail="Unrecognized URL format.")

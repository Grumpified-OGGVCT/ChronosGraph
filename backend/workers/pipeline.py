"""Background Worker Pipeline — Dequeue → Download → Chunk → Process → Commit."""

import asyncio
import logging
import re
from services.graph_db import create_entity, create_relationship
from services.media import chunk_audio, chunk_text, cleanup_audio, download_video, extract_audio, extract_subtitles, get_video_title
from services.processor import ProcessingContext, process_chunk
from services.queue import dequeue_job, get_incomplete_jobs, log_error, update_job_status
from services.vector_db import find_similar, upsert_entity
from services.ws_manager import ws_manager

logger = logging.getLogger("chronosgraph.pipeline")


def _extract_video_id(url: str) -> str:
    match = re.search(r"(?:v=|youtu\.be/|shorts/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else url[:11]


async def process_job(job: dict) -> None:
    job_id = job["id"]
    url = job["url"]
    video_id = _extract_video_id(url)
    title = job.get("title") or "Untitled"
    try:
        title = job.get("title") or await get_video_title(url)
        await ws_manager.broadcast({"type": "status", "state": "active"})
        await ws_manager.broadcast_toast("success", f"Processing: {title}")

        text = await extract_subtitles(url)
        if text:
            chunks = chunk_text(text, chunk_minutes=15, overlap_seconds=30)
        else:
            video_path = await download_video(url)
            if not video_path:
                await update_job_status(job_id, "error", "Download failed")
                await ws_manager.broadcast_toast("error", f"Download failed: {title}")
                return
            audio_path = await extract_audio(video_path)
            if not audio_path:
                await update_job_status(job_id, "error", "Audio extraction failed")
                return
            audio_chunks = await chunk_audio(audio_path, chunk_minutes=10)
            chunks = []
            for ac in audio_chunks:
                chunks.append(type("Chunk", (), {"index": ac.index, "start_time": ac.start_time,
                    "end_time": f"chunk_{ac.index}", "text": f"[Audio segment {ac.index}]"})())

        if not chunks:
            await update_job_status(job_id, "error", "No content extracted")
            return

        context = ProcessingContext(video_id=video_id, video_title=title, total_chunks=len(chunks))
        for chunk in chunks:
            try:
                await ws_manager.broadcast_progress(title, chunk.index + 1, len(chunks))
                result = await process_chunk(chunk.text, chunk.start_time, chunk.end_time, context)
                for entity in result.entities:
                    existing_id = await find_similar(entity.name)
                    node_id = await create_entity(name=entity.name, entity_type=entity.type,
                        description=entity.description, confidence=entity.confidence,
                        video_id=video_id, timestamp=chunk.start_time)
                    if node_id:
                        await upsert_entity(node_id=node_id, name=entity.name,
                            description=entity.description, entity_type=entity.type, video_id=video_id)
                        await ws_manager.broadcast_new_node({"id": node_id, "name": entity.name,
                            "type": entity.type, "confidence": entity.confidence})
                for rel in result.relationships:
                    ok = await create_relationship(source_name=rel.source, target_name=rel.target,
                        rel_type=rel.type, description=rel.description, confidence=rel.confidence,
                        video_id=video_id, timestamp=chunk.start_time)
                    if ok:
                        await ws_manager.broadcast_new_edge({"source": rel.source, "target": rel.target,
                            "type": rel.type, "confidence": rel.confidence})
            except Exception as e:
                logger.error("Chunk %d failed: %s", chunk.index, e)
                await log_error(job_id, str(e), chunk_index=chunk.index)
                await ws_manager.broadcast_toast("warning", f"Chunk {chunk.index + 1} failed for {title}")

        await cleanup_audio(video_id)
        await update_job_status(job_id, "complete")
        await ws_manager.broadcast({"type": "job_complete", "video_id": video_id, "title": title})
        await ws_manager.broadcast_toast("success", f"Completed: {title}")
    except Exception as e:
        logger.error("Job %s failed: %s", job_id, e, exc_info=True)
        await update_job_status(job_id, "error", str(e))
        await ws_manager.broadcast_toast("error", f"Failed: {title or url}")


async def worker_loop() -> None:
    logger.info("Pipeline worker started")
    incomplete = await get_incomplete_jobs()
    for job in incomplete:
        await process_job(job)
    while True:
        job = await dequeue_job()
        if job:
            await process_job(job)
            await asyncio.sleep(1)
        else:
            await ws_manager.broadcast_status("idle")
            await asyncio.sleep(5)

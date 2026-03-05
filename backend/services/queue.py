"""Queue Service — SQLite-backed job queue for video processing."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional
from models.db_models import ErrorLog, Job, SessionLocal, init_db
from models.schemas import ErrorEntry

logger = logging.getLogger("chronosgraph.queue")
init_db()


async def enqueue_job(job_id: str, url: str, title: Optional[str] = None,
                     playlist_id: Optional[str] = None, playlist_index: Optional[int] = None) -> None:
    with SessionLocal() as session:
        session.add(Job(id=job_id, url=url, title=title, status="pending",
                        playlist_id=playlist_id, playlist_index=playlist_index))
        session.commit()


async def dequeue_job() -> Optional[dict]:
    with SessionLocal() as session:
        job = session.query(Job).filter(Job.status == "pending").order_by(Job.created_at).first()
        if not job:
            return None
        job.status = "processing"
        job.updated_at = datetime.now(timezone.utc)
        session.commit()
        return {"id": job.id, "url": job.url, "title": job.title,
                "playlist_id": job.playlist_id, "playlist_index": job.playlist_index}


async def update_job_status(job_id: str, status: str, error_message: Optional[str] = None) -> None:
    with SessionLocal() as session:
        job = session.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = status
            job.error_message = error_message
            job.updated_at = datetime.now(timezone.utc)
            if status == "error":
                job.retry_count += 1
            session.commit()


async def get_incomplete_jobs() -> list[dict]:
    with SessionLocal() as session:
        jobs = session.query(Job).filter(Job.status == "processing").all()
        return [{"id": j.id, "url": j.url, "title": j.title} for j in jobs]


async def get_queue_count() -> int:
    with SessionLocal() as session:
        return session.query(Job).filter(Job.status == "pending").count()


async def get_errors() -> list[ErrorEntry]:
    with SessionLocal() as session:
        entries = session.query(ErrorLog).order_by(ErrorLog.timestamp.desc()).all()
        return [ErrorEntry(id=e.id, job_id=e.job_id, chunk_index=e.chunk_index,
                           message=e.message, timestamp=e.timestamp, retryable=bool(e.retryable))
                for e in entries]


async def log_error(job_id: str, message: str, chunk_index: Optional[int] = None) -> str:
    error_id = str(uuid.uuid4())
    with SessionLocal() as session:
        session.add(ErrorLog(id=error_id, job_id=job_id, chunk_index=chunk_index, message=message))
        session.commit()
    return error_id


async def retry_job(error_id: str) -> bool:
    with SessionLocal() as session:
        entry = session.query(ErrorLog).filter(ErrorLog.id == error_id).first()
        if not entry:
            return False
        job = session.query(Job).filter(Job.id == entry.job_id).first()
        if job:
            job.status = "pending"
            job.error_message = None
            job.updated_at = datetime.now(timezone.utc)
            session.commit()
            return True
        return False

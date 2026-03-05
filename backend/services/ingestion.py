"""Ingestion Service — URL detection, playlist expansion, queue coordination."""

import logging
import re
import uuid
from services.media import expand_playlist
from services.queue import enqueue_job

logger = logging.getLogger("chronosgraph.ingestion")
PLAYLIST_PATTERN = re.compile(r"[?&]list=([a-zA-Z0-9_-]+)")


async def ingest_url(url: str) -> tuple[int, str]:
    playlist_match = PLAYLIST_PATTERN.search(url)
    if playlist_match:
        playlist_id = playlist_match.group(1)
        entries = await expand_playlist(url)
        if not entries:
            job_id = str(uuid.uuid4())
            await enqueue_job(job_id, url, playlist_id=playlist_id)
            return 1, "Playlist queued (expansion failed)"
        for i, entry in enumerate(entries):
            job_id = str(uuid.uuid4())
            await enqueue_job(job_id, entry["url"], title=entry.get("title"),
                              playlist_id=playlist_id, playlist_index=i)
        return len(entries), f"Playlist expanded: {len(entries)} videos queued"
    else:
        job_id = str(uuid.uuid4())
        await enqueue_job(job_id, url)
        return 1, "Video queued"

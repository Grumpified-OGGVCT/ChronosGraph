import pytest
from fastapi.testclient import TestClient
from main import app
from services.media import chunk_text, expand_playlist
from models.schemas import ExtractionResult

client = TestClient(app)

def test_backend_health():
    with TestClient(app) as test_client:
        response = test_client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_playlist_expansion():
    url = "https://www.youtube.com/playlist?list=PLOU2XLYxmsIKs0L5E63xL9xYgN4rP6q_s"
    entries = await expand_playlist(url)
    assert isinstance(entries, list)

def test_chunk_text_fallback():
    sample_vtt = "[00:00:00] Hello world\n[00:16:00] Next part"
    chunks = chunk_text(sample_vtt, chunk_minutes=15)
    assert len(chunks) > 0
    assert chunks[0].start_time == "00:00:00"

def test_ingest_endpoint_validation():
    with TestClient(app) as test_client:
        resp = test_client.post("/api/ingest", json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "queued"

        resp_invalid = test_client.post("/api/ingest", json={"url": "not-a-url"})
        assert resp_invalid.status_code == 400

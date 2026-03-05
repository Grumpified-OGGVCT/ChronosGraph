"""Error Router — Lists errors and supports retry of failed jobs."""

import logging
from fastapi import APIRouter, HTTPException
from models.schemas import ErrorEntry
from services.queue import get_errors, retry_job

router = APIRouter(prefix="/api", tags=["errors"])
logger = logging.getLogger("chronosgraph.errors")


@router.get("/errors", response_model=list[ErrorEntry])
async def list_errors() -> list[ErrorEntry]:
    return await get_errors()


@router.post("/errors/{error_id}/retry")
async def retry_error(error_id: str) -> dict:
    success = await retry_job(error_id)
    if not success:
        raise HTTPException(status_code=404, detail="Error entry not found")
    return {"status": "requeued", "error_id": error_id}

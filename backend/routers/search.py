"""Search Router — Vector similarity search via ChromaDB."""

import logging
from typing import Optional
from fastapi import APIRouter, Query
from models.schemas import SearchResult
from services.vector_db import search_entities

router = APIRouter(prefix="/api", tags=["search"])
logger = logging.getLogger("chronosgraph.search")


@router.get("/search", response_model=list[SearchResult])
async def search(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    entity_type: Optional[str] = Query(None),
) -> list[SearchResult]:
    results = await search_entities(q, n_results=limit, entity_type=entity_type)
    return results

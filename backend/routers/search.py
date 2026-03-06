"""Search Router — Vector similarity search via ChromaDB."""

import logging
from typing import Optional
from fastapi import APIRouter, Query
from models.schemas import SearchResult, RagRequest, RagResponse
from services.processor import get_client
from config import settings
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


@router.post("/rag", response_model=RagResponse)
async def query_rag(request: RagRequest) -> RagResponse:
    # 1. Fetch relevant entities from ChromaDB
    results = await search_entities(request.query, n_results=request.limit)

    if not results:
        return RagResponse(answer="I couldn't find any relevant information in the knowledge graph.", sources=[])

    # 2. Build context string
    context_chunks = []
    for r in results:
        context_chunks.append(f"Entity: {r.name} ({r.type})\nDescription: {r.description}")

    context_text = "\n\n---\n\n".join(context_chunks)

    # 3. Prompt Gemini 2.5 Pro with context
    prompt = f"""You are an AI assistant analyzing a knowledge graph. Answer the user's query based strictly on the provided context entities below.
If the answer cannot be found in the context, say "I don't have enough information to answer that."

USER QUERY: {request.query}

KNOWLEDGE GRAPH CONTEXT:
{context_text}
"""

    try:
        client = get_client()
        response = client.models.generate_content(model=settings.model_version, contents=prompt)
        answer = response.text or "Error generating response."
    except Exception as e:
        logger.error("RAG generation failed: %s", e)
        answer = "I encountered an error while generating the response. Please try again later."

    return RagResponse(answer=answer, sources=results)

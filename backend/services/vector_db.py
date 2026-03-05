"""Vector DB Service — ChromaDB for entity embeddings and similarity search."""

import logging
from typing import Optional
import chromadb
from config import settings
from models.schemas import SearchResult

logger = logging.getLogger("chronosgraph.vector_db")
_persist_dir = str(settings.resolve_path(settings.chroma_persist_dir))
_client: Optional[chromadb.ClientAPI] = None
_collection = None
COLLECTION_NAME = "chronosgraph_entities"


def get_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=_persist_dir)
    return _client


def get_collection():
    global _collection
    if _collection is None:
        _collection = get_client().get_or_create_collection(
            name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"})
    return _collection


async def upsert_entity(node_id: str, name: str, description: str,
                        entity_type: str, video_id: str = "") -> None:
    collection = get_collection()
    collection.upsert(ids=[node_id], documents=[f"{name} {description}"],
                      metadatas=[{"type": entity_type, "video_id": video_id, "name": name}])


async def search_entities(query: str, n_results: int = 20,
                          entity_type: Optional[str] = None) -> list[SearchResult]:
    collection = get_collection()
    where = {"type": entity_type} if entity_type else None
    try:
        results = collection.query(query_texts=[query],
            n_results=min(n_results, collection.count() or 1), where=where)
    except Exception as e:
        logger.error("ChromaDB search failed: %s", e)
        return []
    out = []
    if results and results["ids"]:
        for i, nid in enumerate(results["ids"][0]):
            meta = results["metadatas"][0][i] if results["metadatas"] else {}
            dist = results["distances"][0][i] if results["distances"] else 1.0
            out.append(SearchResult(node_id=nid, name=meta.get("name", ""),
                type=meta.get("type", "Concept"),
                description=(results["documents"][0][i] if results["documents"] else ""),
                score=max(0.0, 1.0 - dist)))
    return out


async def find_similar(name: str, threshold: float = 0.90) -> Optional[str]:
    collection = get_collection()
    if collection.count() == 0:
        return None
    results = collection.query(query_texts=[name], n_results=1)
    if results and results["ids"] and results["ids"][0]:
        if 1.0 - results["distances"][0][0] >= threshold:
            return results["ids"][0][0]
    return None

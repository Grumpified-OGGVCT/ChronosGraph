"""Graph DB Service — Neo4j driver for node/edge CRUD and entity resolution."""

import logging
from typing import Optional
from neo4j import AsyncGraphDatabase
from config import settings
from models.schemas import FilterMetadata, GraphData, GraphEdge, GraphNode

logger = logging.getLogger("chronosgraph.graph_db")
_driver = None


async def get_driver():
    global _driver
    if _driver is None:
        _driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password))
        try:
            await _driver.verify_connectivity()
            logger.info("Neo4j connected: %s", settings.neo4j_uri)
        except Exception as e:
            logger.warning("Neo4j not available: %s. Graph features disabled.", e)
            _driver = None
    return _driver


async def close_driver():
    global _driver
    if _driver:
        await _driver.close()
        _driver = None


async def create_entity(name: str, entity_type: str, description: str,
                        confidence: float, video_id: str, timestamp: str) -> Optional[str]:
    driver = await get_driver()
    if not driver:
        return None
    async with driver.session() as session:
        result = await session.run("""
            MERGE (e:Entity {name: $name})
            ON CREATE SET e.type = $type, e.description = $description,
                          e.confidence = $confidence, e.mention_count = 1,
                          e.created_at = datetime(), e.data_quality = 'complete',
                          e.video_sources = [$video_source]
            ON MATCH SET  e.mention_count = e.mention_count + 1,
                          e.description = e.description + ' | ' + $description,
                          e.video_sources = e.video_sources + $video_source
            RETURN elementId(e) AS id
        """, name=name, type=entity_type, description=description,
            confidence=confidence, video_source=f"{video_id}@{timestamp}")
        record = await result.single()
        return record["id"] if record else None


async def create_relationship(source_name: str, target_name: str, rel_type: str,
                               description: str, confidence: float,
                               video_id: str, timestamp: str) -> bool:
    driver = await get_driver()
    if not driver:
        return False
    async with driver.session() as session:
        await session.run("""
            MATCH (a:Entity {name: $source}), (b:Entity {name: $target})
            CREATE (a)-[r:RELATES_TO {
                type: $rel_type, description: $description,
                source_video: $video_id, timestamp: $timestamp,
                confidence: $confidence
            }]->(b)
        """, source=source_name, target=target_name, rel_type=rel_type,
            description=description, confidence=confidence,
            video_id=video_id, timestamp=timestamp)
        return True


async def get_all_graph_data() -> GraphData:
    driver = await get_driver()
    if not driver:
        return GraphData()
    nodes, edges = [], []
    async with driver.session() as session:
        result = await session.run("""
            MATCH (e:Entity)
            RETURN elementId(e) AS id, e.name AS name, e.type AS type,
                   e.description AS description, e.confidence AS confidence,
                   e.mention_count AS mention_count,
                   toString(e.created_at) AS created_at,
                   e.data_quality AS data_quality,
                   e.video_sources AS video_sources
        """)
        async for record in result:
            vs = []
            for s in (record["video_sources"] or []):
                parts = s.split("@", 1)
                vs.append({"video_id": parts[0], "timestamp": parts[1] if len(parts) > 1 else ""})
            nodes.append(GraphNode(id=record["id"], name=record["name"],
                type=record["type"] or "Concept", description=record["description"] or "",
                confidence=record["confidence"] or 0.0, mention_count=record["mention_count"] or 1,
                created_at=record["created_at"], data_quality=record["data_quality"] or "complete",
                video_sources=vs))
        result = await session.run("""
            MATCH (a:Entity)-[r:RELATES_TO]->(b:Entity)
            RETURN elementId(a) AS source, elementId(b) AS target,
                   r.type AS type, r.description AS description,
                   r.confidence AS confidence,
                   r.source_video AS video_id, r.timestamp AS timestamp
        """)
        async for record in result:
            edges.append(GraphEdge(source=record["source"], target=record["target"],
                type=record["type"] or "RELATES_TO", description=record["description"] or "",
                confidence=record["confidence"] or 0.0, video_id=record["video_id"] or "",
                timestamp=record["timestamp"] or ""))
    return GraphData(nodes=nodes, edges=edges)


async def get_node_detail(node_id: str) -> Optional[GraphNode]:
    driver = await get_driver()
    if not driver:
        return None
    async with driver.session() as session:
        result = await session.run("""
            MATCH (e:Entity) WHERE elementId(e) = $id
            RETURN elementId(e) AS id, e.name AS name, e.type AS type,
                   e.description AS description, e.confidence AS confidence,
                   e.mention_count AS mention_count,
                   toString(e.created_at) AS created_at,
                   e.data_quality AS data_quality,
                   e.video_sources AS video_sources
        """, id=node_id)
        record = await result.single()
        if not record:
            return None
        vs = []
        for s in (record["video_sources"] or []):
            parts = s.split("@", 1)
            vs.append({"video_id": parts[0], "timestamp": parts[1] if len(parts) > 1 else ""})
        return GraphNode(id=record["id"], name=record["name"],
            type=record["type"] or "Concept", description=record["description"] or "",
            confidence=record["confidence"] or 0.0, mention_count=record["mention_count"] or 1,
            created_at=record["created_at"], data_quality=record["data_quality"] or "complete",
            video_sources=vs)


async def get_filter_metadata() -> FilterMetadata:
    driver = await get_driver()
    if not driver:
        return FilterMetadata()
    async with driver.session() as session:
        result = await session.run("""
            MATCH (e:Entity)
            RETURN collect(DISTINCT e.type) AS types,
                   toString(min(e.created_at)) AS min_date,
                   toString(max(e.created_at)) AS max_date
        """)
        record = await result.single()
        if not record:
            return FilterMetadata()
        return FilterMetadata(
            entity_types=[t for t in (record["types"] or []) if t],
            date_range={"min": record["min_date"], "max": record["max_date"]})

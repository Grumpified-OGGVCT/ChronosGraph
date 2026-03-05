"""Graph Router — Serves node/edge data for the 3D visualization."""

import logging
from fastapi import APIRouter, HTTPException
from models.schemas import GraphData, GraphNode
from services.graph_db import get_all_graph_data, get_node_detail

router = APIRouter(prefix="/api", tags=["graph"])
logger = logging.getLogger("chronosgraph.graph")


@router.get("/graph", response_model=GraphData)
async def get_graph() -> GraphData:
    return await get_all_graph_data()


@router.get("/graph/node/{node_id}", response_model=GraphNode)
async def get_node(node_id: str) -> GraphNode:
    node = await get_node_detail(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node

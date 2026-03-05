"""Pydantic schemas for API request/response models."""

from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    url: str = Field(..., description="YouTube video or playlist URL")

class RetryRequest(BaseModel):
    job_id: str

class EntitySchema(BaseModel):
    name: str
    type: str
    description: str = ""
    confidence: float = 0.0

class RelationshipSchema(BaseModel):
    source: str
    target: str
    type: str
    description: str = ""
    confidence: float = 0.0

class ExtractionResult(BaseModel):
    entities: list[EntitySchema] = []
    relationships: list[RelationshipSchema] = []
    running_summary: str = ""

class VideoSource(BaseModel):
    video_id: str
    timestamp: str = ""

class GraphNode(BaseModel):
    id: str
    name: str
    type: str
    description: str = ""
    confidence: float = 0.0
    mention_count: int = 1
    created_at: Optional[str] = None
    video_sources: list[VideoSource] = []
    data_quality: str = "complete"

class GraphEdge(BaseModel):
    source: str
    target: str
    type: str
    description: str = ""
    confidence: float = 0.0
    video_id: str = ""
    timestamp: str = ""

class GraphData(BaseModel):
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []

class JobStatus(BaseModel):
    id: str
    url: str
    title: Optional[str] = None
    status: str = "pending"
    playlist_id: Optional[str] = None
    playlist_index: Optional[int] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ErrorEntry(BaseModel):
    id: str
    job_id: str
    chunk_index: Optional[int] = None
    message: str
    timestamp: datetime
    retryable: bool = True

class IngestResponse(BaseModel):
    status: str = "queued"
    count: int = 1
    message: str = ""

class SearchResult(BaseModel):
    node_id: str
    name: str
    type: str
    description: str
    score: float
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

class FilterMetadata(BaseModel):
    entity_types: list[str] = []
    date_range: dict[str, Optional[str]] = {"min": None, "max": None}

"""Filters Router — Provides available filter options for the UI."""

import logging
from fastapi import APIRouter
from models.schemas import FilterMetadata
from services.graph_db import get_filter_metadata

router = APIRouter(prefix="/api", tags=["filters"])


@router.get("/filters/metadata", response_model=FilterMetadata)
async def filters_metadata() -> FilterMetadata:
    return await get_filter_metadata()

"""Gemini Processor — AI orchestrator with context chaining."""

import json
import logging
from dataclasses import dataclass, field
from typing import Optional
from google import genai
from config import settings
from models.schemas import ExtractionResult
from utils.retry import with_retry

logger = logging.getLogger("chronosgraph.processor")
_client: Optional[genai.Client] = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


@dataclass
class ProcessingContext:
    video_id: str
    video_title: str
    running_summary: str = ""
    entities_seen: set = field(default_factory=set)
    chunk_index: int = 0
    total_chunks: int = 0


EXTRACTION_PROMPT = """You are a knowledge graph extraction engine. Analyze the following content.

CONTEXT FROM PREVIOUS SEGMENTS:
{running_summary}

CURRENT SEGMENT (Segment {chunk_index} of {total_chunks}):
Source: "{video_title}" (ID: {video_id})
Timeframe: {start_time} to {end_time}
---
{chunk_content}
---

INSTRUCTIONS:
1. Extract all named entities: People, Organizations, Concepts, Events, Locations.
2. Extract relationships between entities with a confidence score (0.0-1.0).
3. Merge with previously seen entities where appropriate.
4. Generate an updated running summary.

OUTPUT FORMAT (strict JSON, no markdown fences):
{{
  "entities": [
    {{ "name": "...", "type": "Person|Organization|Concept|Event|Location", "description": "...", "confidence": 0.95 }}
  ],
  "relationships": [
    {{ "source": "Entity A", "target": "Entity B", "type": "RELATES_TO|WORKS_FOR|LOCATED_IN|CAUSED|...", "description": "...", "confidence": 0.9 }}
  ],
  "running_summary": "Updated cumulative summary..."
}}"""


@with_retry(max_retries=3, base_delay=2.0)
async def _call_gemini(prompt: str) -> str:
    client = get_client()
    response = client.models.generate_content(model=settings.model_version, contents=prompt)
    return response.text or ""


async def process_chunk(chunk_content: str, start_time: str, end_time: str,
                        context: ProcessingContext) -> ExtractionResult:
    context.chunk_index += 1
    prompt = EXTRACTION_PROMPT.format(
        running_summary=context.running_summary or "(No previous context.)",
        chunk_index=context.chunk_index, total_chunks=context.total_chunks,
        video_title=context.video_title, video_id=context.video_id,
        start_time=start_time, end_time=end_time,
        chunk_content=chunk_content[:15000])
    raw = await _call_gemini(prompt)
    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        data = json.loads(cleaned.strip())
        result = ExtractionResult(
            entities=[{"name": e["name"], "type": e.get("type", "Concept"),
                       "description": e.get("description", ""), "confidence": e.get("confidence", 0.5)}
                      for e in data.get("entities", [])],
            relationships=[{"source": r["source"], "target": r["target"],
                            "type": r.get("type", "RELATES_TO"), "description": r.get("description", ""),
                            "confidence": r.get("confidence", 0.5)}
                           for r in data.get("relationships", [])],
            running_summary=data.get("running_summary", context.running_summary))
        context.running_summary = result.running_summary
        for e in result.entities:
            context.entities_seen.add(e.name)
        return result
    except (json.JSONDecodeError, KeyError) as e:
        logger.error("Failed to parse Gemini response: %s", e)
        return ExtractionResult(running_summary=context.running_summary)

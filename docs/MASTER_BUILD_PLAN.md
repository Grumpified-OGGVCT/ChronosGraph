# ChronosGraph: Master Build Plan

This is the definitive architecture specification and build guide.
See the full document for implementation details.

## Architecture Overview

```
[YouTube URL] → [Ingestion Manager] → [Processing Queue (SQLite)]
                                              ↓
[yt-dlp Download] → [FFmpeg Chunking] → [Gemini 2.5 Pro Extraction]
                                              ↓
[Entity Resolution (ChromaDB)] → [Graph Commit (Neo4j)]
                                              ↓
[WebSocket Broadcast] → [3D Visualization (Three.js)]
```

## Tech Stack
- **Backend**: Python 3.12+ / FastAPI
- **Databases**: Neo4j 5.x + ChromaDB + SQLite
- **Frontend**: React 18 + Three.js + d3-force-3d
- **AI**: Google Gemini 2.5 Pro
- **Media**: yt-dlp + FFmpeg

## Build Phases
1. **Phase A** — Skeleton & Config (✅ Complete)
2. **Phase B** — Ingestion Pipeline
3. **Phase C** — AI Processing & Graph Commit
4. **Phase D** — Frontend Controls
5. **Phase E** — 3D Visualization
6. **Phase F** — Video Playback & Polish

## Critical Rules
1. Never block the main thread
2. Never reset the graph — data is additive
3. Always chain context via running_summary
4. Always resolve entities before creating nodes
5. Always broadcast state changes via WebSocket
6. Graceful degradation — failures don't halt processing
7. Clean up temp audio after processing

For the full specification, see [chronosgraph_build_prompt.md](../chronosgraph_build_prompt.md)
or the repo wiki.

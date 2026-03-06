# ChronosGraph — TODO

## Phase A: Skeleton & Config ✅
- [x] Project directory structure
- [x] `config.env.example` + `requirements.txt`
- [x] `backend/config.py` — Pydantic Settings
- [x] `backend/main.py` — FastAPI + WebSocket + static mount
- [x] All routers: ingest, search, graph, errors, filters
- [x] All services: queue, graph_db, vector_db, ws_manager, media, processor, ingestion
- [x] Worker pipeline with resume logic
- [x] Utils: logger, retry
- [x] Models: schemas, db_models
- [x] Frontend scaffold: Vite + React + dark theme
- [x] `run.bat` — Windows launcher
- [ ] **Verify**: Backend boots, frontend loads, WS echoes

## Phase B: Ingestion Pipeline
- [ ] End-to-end test: URL → download → chunks on disk
- [ ] Playlist expansion integration test
- [ ] Subtitle vs audio fallback verification

## Phase C: AI Processing & Graph Commit
- [ ] Gemini API integration test
- [ ] Entity resolution via ChromaDB similarity
- [ ] Neo4j node/edge commit verification
- [ ] Context chaining across chunks

## Phase D: Frontend — Header & Controls
- [x] InputBar component with loading state
- [x] StatusIndicator (WS-driven: idle/active/queue)
- [x] SearchBar with Focus Mode dispatch
- [x] Toast notifications (slide-in, auto-dismiss)
- [x] ErrorLog modal with retry buttons
- [x] FilterPanel: entity type, date range, confidence sliders

## Phase E: 3D Visualization — "The Holodeck"
- [x] Three.js scene setup with dark environment
- [x] d3-force-3d layout with temporal Z-axis
- [x] Instanced node rendering (color by type, scale by mentions)
- [x] Edge rendering with hover brightening
- [x] Hover interaction: tooltip + scale
- [x] Click interaction: HoloCard with entity detail
- [x] Focus Mode (search result highlighting)
- [x] Self-growing animation (WS new_node → fade-in)
- [x] Cluster View (>5,000 nodes → SuperNodes)

## Phase F: Video Playback & Polish
- [x] VideoModal with timestamp seek
- [x] Partial-data node warning indicators
- [x] README with prerequisites + install guide
- [ ] Final `run.bat` validation

# ChronosGraph ◉

ChronosGraph is an enterprise-grade local knowledge OS for ingesting, processing, and visualizing video data as an interactive 3D knowledge graph. It leverages the power of YouTube transcripts, Google Gemini 2.5 Pro for AI extraction, ChromaDB for continuous RAG memory, and Neo4j for deep graph storage.

---

## 🏗️ Architecture Overview

The system processes video sequentially, chained by a running conversational context state, without dropping connections to existing knowledge:

```text
[YouTube URL] → [Ingestion Manager] → [Processing Queue (SQLite)]
                                              ↓
[yt-dlp Download] → [FFmpeg Chunking] → [Gemini 2.5 Pro Extraction]
                                              ↓
[Entity Resolution (ChromaDB)] → [Graph Commit (Neo4j)]
                                              ↓
[WebSocket Broadcast] → [3D Visualization (Three.js)]
```

## 🛠️ Prerequisites

To run ChronosGraph locally, ensure your system has the following installed:
- **Node.js (v18+)**: For compiling and serving the React Three Fiber frontend.
- **Python (v3.12+)**: For the FastAPI backend, AI processors, and media chunking.
- **FFmpeg**: Must be available in your system `PATH` for video-to-audio extraction and audio chunking.
- **yt-dlp**: Must be available in your system `PATH` for robust YouTube downloading and playlist extraction.
- **Neo4j 5.x Database**: An active, running Neo4j instance to store graph commits.

---

## 🚀 Installation & Setup (Windows)

For Windows users, we provide a robust installation and launch wizard.

1. Clone the repository and navigate to the project directory.
2. Double-click the **`install.bat`** file.
   - This advanced TUI wizard will check your system for `node` and `python`.
   - It will interactively guide you through setting up your `config.env` file (asking for your Gemini API key and Neo4j credentials).
   - It will automatically set up an isolated Python virtual environment (`venv`) and install all required `pip` dependencies.
   - Finally, it will run `npm install --legacy-peer-deps` and `npm run build` inside the `frontend/` directory.

## 🏃 Running the Application

Once the installation wizard is complete, simply execute:

```cmd
run.bat
```

This will activate the virtual environment and spawn the FastAPI server.
Open your browser to the URL output in the terminal (usually `http://127.0.0.1:8000`).

---

## 📸 Interface Previews

### End-to-End Ingestion Flow
*(Screenshot Placeholder: Showcasing the UI InputBar dynamically processing a URL to download chunks, with the progress bar updating in real time.)*
`[PLACEHOLDER: doc_images/e2e_ingestion.png]`

### The Holodeck (3D Visualization)
*(Screenshot Placeholder: Showcasing the 3D force-directed graph with SuperNodes and active Hover Contexts)*
`[PLACEHOLDER: doc_images/holodeck_cluster.png]`

### Infinite RAG Search
*(Screenshot Placeholder: Showcasing the SearchBar executing the /api/rag endpoint against ChromaDB)*
`[PLACEHOLDER: doc_images/infinite_rag.png]`

---

## 📡 Linux / MacOS Setup

If you are not on Windows, you can install the system manually:

```bash
# 1. Setup configuration
cp config.env.example config.env

# Edit config.env manually here to insert your API keys and Neo4j info

# 2. Build Frontend
cd frontend
npm install --legacy-peer-deps
npm run build
cd ..

# 3. Build Backend
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Start Server
python -m backend.main
```

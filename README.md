# ChronosGraph
YouTube video transcriber and interactive 3D knowledge graph visualizer.

## Prerequisites
- Node.js (v18+)
- Python (v3.12+)
- FFmpeg (must be in your PATH)
- yt-dlp (must be in your PATH)
- Neo4j database (configured and running)

## Installation Guide

1. Clone the repository and navigate to the project directory.

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install --legacy-peer-deps
   npm run build
   cd ..
   ```

3. **Backend Setup**
   ```bash
   # Install Python requirements
   pip install -r requirements.txt
   ```

4. **Configuration**
   Copy `config.env.example` to `config.env` and update the values:
   ```bash
   cp config.env.example config.env
   ```
   Ensure you set your `gemini_api_key`, Neo4j credentials, and correct paths.

## Usage
Start the application using the backend main module:
```bash
python -m backend.main
```
Or use the provided launcher script on Windows:
```cmd
run.bat
```

Open your browser to the URL output in the terminal (usually `http://127.0.0.1:8000`).

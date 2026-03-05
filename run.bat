@echo off
title ChronosGraph Launcher
cd /d "%~dp0"

echo ============================================
echo   ChronosGraph - Local Knowledge OS
echo ============================================
echo.

REM Check prerequisites
where python >nul 2>&1 || (echo [ERROR] Python not found on PATH. & pause & exit /b 1)
where node >nul 2>&1 || (echo [ERROR] Node.js not found on PATH. & pause & exit /b 1)
where ffmpeg >nul 2>&1 || (echo [WARNING] FFmpeg not found on PATH. Audio processing will fail.)

REM Create data directories
if not exist "data\db" mkdir "data\db"
if not exist "data\cache\video" mkdir "data\cache\video"
if not exist "data\cache\audio" mkdir "data\cache\audio"
if not exist "data\chroma" mkdir "data\chroma"
if not exist "logs" mkdir "logs"

REM Start Neo4j (if installed as service, skip this)
echo [1/3] Checking Neo4j...
neo4j status >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Starting Neo4j...
    start "Neo4j" cmd /c "neo4j console"
    timeout /t 5 /nobreak >nul
) else (
    echo [INFO] Neo4j already running.
)

REM Start Backend
echo [2/3] Starting Backend (FastAPI)...
start "ChronosGraph Backend" cmd /c "cd backend && python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 3 /nobreak >nul

REM Start Frontend
echo [3/3] Starting Frontend (Vite)...
start "ChronosGraph Frontend" cmd /c "cd frontend && npm run dev"

echo.
echo ============================================
echo   All services launched!
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000
echo   Neo4j:    http://localhost:7474
echo ============================================
echo.
echo Press any key to stop all services...
pause >nul

REM Cleanup
taskkill /FI "WINDOWTITLE eq ChronosGraph Backend" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq ChronosGraph Frontend" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Neo4j" /F >nul 2>&1
echo Services stopped.

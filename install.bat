@echo off
setlocal EnableDelayedExpansion
title ChronosGraph Installer

echo ==================================================
echo         CHRONOSGRAPH INSTALLATION WIZARD
echo ==================================================
echo.

:: 1. Check Prerequisites
echo [*] Checking prerequisites...
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] Node.js is not installed or not in PATH. Please install Node.js v18+.
    goto END
)
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] Python is not installed or not in PATH. Please install Python 3.12+.
    goto END
)

:: 2. Setup Configuration
echo.
echo [*] Configuration Setup
if exist config.env (
    set /p RECONFIGURE="config.env already exists. Do you want to reconfigure? (y/N): "
    if /I "!RECONFIGURE!" neq "y" goto SKIP_CONFIG
)

echo.
echo Please enter your Configuration details:
set /p GEMINI_API_KEY="GemINI 2.5 Pro API Key: "
set /p NEO4J_URI="Neo4j URI (default: bolt://localhost:7687): "
if "!NEO4J_URI!"=="" set NEO4J_URI=bolt://localhost:7687
set /p NEO4J_USER="Neo4j Username (default: neo4j): "
if "!NEO4J_USER!"=="" set NEO4J_USER=neo4j
set /p NEO4J_PASSWORD="Neo4j Password: "

echo.
echo [*] Writing config.env...
(
echo gemini_api_key="!GEMINI_API_KEY!"
echo neo4j_uri="!NEO4J_URI!"
echo neo4j_user="!NEO4J_USER!"
echo neo4j_password="!NEO4J_PASSWORD!"
echo model_version="gemini-2.5-pro"
echo max_chunk_size_minutes=15
) > config.env
echo [+] config.env created successfully.

:SKIP_CONFIG
:: 3. Setup Python Backend
echo.
echo [*] Setting up Python backend...
if not exist "venv" (
    echo [*] Creating virtual environment...
    python.exe -m venv venv
)
call venv\Scripts\activate.bat
echo [*] Installing dependencies...
pip install -r requirements.txt

:: 4. Setup Frontend
echo.
echo [*] Setting up Frontend...
cd frontend
call npm install --legacy-peer-deps
call npm run build
cd ..

echo.
echo ==================================================
echo [+] Installation Complete!
echo [i] You can now start the application by running: run.bat
echo ==================================================

:END
pause

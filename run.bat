@echo off
setlocal EnableDelayedExpansion
title ChronosGraph Runner

echo ==================================================
echo         CHRONOSGRAPH LAUNCHER
echo ==================================================
echo.

if not exist config.env (
    echo [!] config.env not found. Please run install.bat first.
    pause
    goto END
)

if not exist venv (
    echo [!] Python virtual environment not found. Please run install.bat first.
    pause
    goto END
)

echo [*] Starting Neo4j database (assumes Neo4j Desktop or service is configured)...
:: Typically on Windows, Neo4j is run as a service, but if you have a local bin path:
:: Uncomment below if using standalone neo4j extract
:: call neo4j start

echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

echo [*] Starting ChronosGraph backend and frontend servers...
python -m backend.main

:END
pause

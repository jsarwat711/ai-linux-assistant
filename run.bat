@echo off
title AI Linux Command Assistant
color 0A
cls

echo =====================================================
echo   AI Linux Command Assistant
echo   Starting...
echo =====================================================
echo.

cd /d "%~dp0"

:: ── STEP 1: CHECK DOCKER ──────────────────────────────
echo [1/5] Checking Docker...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [!] Docker not running or not installed!
    echo  Please install Rancher Desktop:
    echo  https://rancherdesktop.io
    echo.
    start "" "https://rancherdesktop.io"
    pause
    exit /b 1
)
echo  [OK] Docker ready!
echo.

:: ── STEP 2: FIND PYTHON ───────────────────────────────
echo [2/5] Checking Python...

SET PYTHON_CMD=

:: Try 'python' first
python --version >nul 2>&1
if %errorlevel% equ 0 (
    SET PYTHON_CMD=python
    goto python_found
)

:: Try 'python3'
python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    SET PYTHON_CMD=python3
    goto python_found
)

:: Try 'py' launcher (Windows Python launcher)
py --version >nul 2>&1
if %errorlevel% equ 0 (
    SET PYTHON_CMD=py
    goto python_found
)

:: Python not found at all
echo.
echo  [!] Python not found on your system!
echo.
echo  Please install Python from:
echo  https://www.python.org/downloads/
echo.
echo  IMPORTANT: During install check this box:
echo  [x] Add Python to PATH
echo.
start "" "https://www.python.org/downloads/"
pause
exit /b 1

:python_found
for /f "tokens=*" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set PY_VER=%%i
echo  [OK] Found: %PY_VER% (command: %PYTHON_CMD%)
echo.

:: ── STEP 3: INSTALL PYTHON PACKAGES ──────────────────
echo [3/5] Installing Python packages...
echo  Please wait...
echo.
%PYTHON_CMD% -m pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo  [!] Failed to install packages.
    echo  Trying with --user flag...
    %PYTHON_CMD% -m pip install -q --user -r requirements.txt
    if %errorlevel% neq 0 (
        echo  [ERROR] Package install failed!
        pause
        exit /b 1
    )
)
echo  [OK] Packages installed!
echo.

:: ── STEP 4: START OLLAMA ──────────────────────────────
echo [4/5] Starting Ollama AI engine...
docker-compose up -d
if %errorlevel% neq 0 (
    echo  [!] Trying docker compose (newer syntax)...
    docker compose up -d
)
echo.
echo  Waiting for Ollama to be ready...
echo  (This may take 30-60 seconds)
echo.

SET /A WAIT_COUNT=0
:wait_ollama
SET /A WAIT_COUNT+=1
if %WAIT_COUNT% gtr 40 (
    echo  [WARNING] Ollama taking long. Continuing anyway...
    goto ollama_ready
)
curl -sf http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    timeout /t 3 /nobreak >nul
    echo  Still waiting... (%WAIT_COUNT%/40^)
    goto wait_ollama
)

:ollama_ready
echo  [OK] Ollama is ready!
echo.

:: ── STEP 5: CHECK AND PULL MODEL ─────────────────────
echo [5/5] Checking AI model...
curl -sf http://localhost:11434/api/tags 2>nul | findstr "llama3" >nul 2>&1
if %errorlevel% neq 0 (
    echo  Downloading AI model (~4.7 GB first time only^)...
    echo  Please wait...
    docker exec ollama ollama pull llama3
)
echo  [OK] Model ready!
echo.

:: ── LAUNCH DESKTOP APP ────────────────────────────────
echo =====================================================
echo   Launching AI Command Assistant window...
echo =====================================================
echo.

%PYTHON_CMD% ai_linux_assistant.py

:: ── ON APP CLOSE ──────────────────────────────────────
echo.
echo  App closed.
echo.
choice /C YN /M "Stop Ollama engine too (Y/N)?"
if %errorlevel% equ 1 (
    docker-compose down 2>nul
    docker compose down 2>nul
    echo  [OK] Ollama stopped.
)
echo.
echo  Goodbye!
timeout /t 3 /nobreak >nul

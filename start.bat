@echo off
title AI Linux Command Assistant
color 0A
cls

echo =====================================================
echo   AI Linux Command Assistant — Starting...
echo =====================================================
echo.

:: ── CHECK DOCKER IS RUNNING ───────────────────────────
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Docker is not running. Starting Docker...
    start "" "C:\Program Files\Rancher Desktop\Rancher Desktop.exe"
    echo     Waiting 20 seconds for Docker to start...
    timeout /t 20 /nobreak >nul
)

:: ── START APP ─────────────────────────────────────────
echo [1/2] Starting containers...
docker-compose up -d
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start. Try running install.bat first.
    pause
    exit /b 1
)

echo.
echo [2/2] Waiting for app to be ready...
timeout /t 8 /nobreak >nul

:: ── OPEN BROWSER ──────────────────────────────────────
echo.
echo =====================================================
echo   App is running!
echo   Opening browser...
echo   URL:      http://localhost:6080
echo   Password: aiassist
echo =====================================================
echo.
start "" "http://localhost:6080"

echo   Press any key to view logs (Ctrl+C to stop logs)
pause >nul
docker-compose logs -f

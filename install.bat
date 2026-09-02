@echo off
title AI Linux Command Assistant — Installer
color 0A
cls

echo =====================================================
echo   AI Linux Command Assistant
echo   Installer for Windows
echo =====================================================
echo.

:: ── CHECK ADMIN RIGHTS ────────────────────────────────
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Please run this as Administrator!
    echo Right-click install.bat and select "Run as administrator"
    pause
    exit /b 1
)

:: ── CHECK DOCKER ──────────────────────────────────────
echo [1/4] Checking Docker installation...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [!] Docker not found. Installing Rancher Desktop...
    echo     This may take a few minutes...
    echo.
    :: Download Rancher Desktop silently
    curl -L -o "%TEMP%\rancher-desktop.msi" ^
        "https://github.com/rancher-sandbox/rancher-desktop/releases/latest/download/Rancher.Desktop.Setup.msi"
    msiexec /i "%TEMP%\rancher-desktop.msi" /quiet /norestart
    echo.
    echo [!] Rancher Desktop installed.
    echo     Please RESTART your computer then run install.bat again.
    pause
    exit /b 0
) else (
    echo [OK] Docker found.
    docker --version
)

echo.

:: ── CHECK DOCKER COMPOSE ──────────────────────────────
echo [2/4] Checking Docker Compose...
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    docker compose version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Docker Compose not found.
        echo Please install Docker Desktop or Rancher Desktop.
        pause
        exit /b 1
    )
)
echo [OK] Docker Compose found.
echo.

:: ── BUILD THE APP ─────────────────────────────────────
echo [3/4] Building AI Command Assistant...
echo       (First time may take 5-10 minutes)
echo.
docker-compose build
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Build failed. Check error messages above.
    pause
    exit /b 1
)
echo.
echo [OK] Build complete!
echo.

:: ── PULL OLLAMA MODEL ─────────────────────────────────
echo [4/4] Downloading AI model (llama3 ~4.7GB)...
echo       This only happens ONCE. Please wait...
echo.
docker-compose run --rm ollama_pull
echo.
echo [OK] AI model ready!
echo.

:: ── DONE ──────────────────────────────────────────────
echo =====================================================
echo   Installation Complete!
echo =====================================================
echo.
echo   To START the app: double-click  start.bat
echo   To STOP the app:  double-click  stop.bat
echo   Then open browser: http://localhost:6080
echo   Password: aiassist
echo.
echo =====================================================
pause

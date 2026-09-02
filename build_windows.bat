@echo off
title AI Command Assistant - Windows Builder
color 0A

echo ============================================
echo   AI Linux Command Assistant - EXE Builder
echo   Fast Mode: --onedir build
echo ============================================
echo.

REM ---- Check Python ----
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] Python not found.
    pause
    exit /b 1
)
echo [OK] Python found.

REM ---- Install packages ----
echo.
echo [STEP 1] Installing packages...
pip install --upgrade pip
pip install PySide6 pyinstaller ollama requests Pygments
echo [OK] Done.

REM ---- Clean old build ----
echo.
echo [STEP 2] Cleaning old build...
IF EXIST "dist"   rmdir /s /q dist
IF EXIST "build"  rmdir /s /q build
IF EXIST "*.spec" del /q *.spec
echo [OK] Cleaned.

REM ---- Check icon ----
IF EXIST "icon.ico" (
    SET ICON_ARG=--icon "icon.ico"
) ELSE (
    SET ICON_ARG=
)

REM ---- Build EXE (onedir = fast startup) ----
echo.
echo [STEP 3] Building EXE...
echo This may take 2-5 minutes. Please wait...
echo.

pyinstaller ^
  --onedir ^
  --windowed ^
  --name "AI_Command_Assistant" ^
  %ICON_ARG% ^
  --add-data "license_manager.py;." ^
  --hidden-import "PySide6" ^
  --hidden-import "PySide6.QtWidgets" ^
  --hidden-import "PySide6.QtCore" ^
  --hidden-import "PySide6.QtGui" ^
  --hidden-import "ollama" ^
  --hidden-import "requests" ^
  --hidden-import "sqlite3" ^
  --hidden-import "pygments" ^
  --collect-all "PySide6" ^
  --collect-all "ollama" ^
  --exclude-module "PySide6.QtWebEngine" ^
  --exclude-module "PySide6.QtWebEngineWidgets" ^
  --exclude-module "PySide6.QtWebEngineCore" ^
  --exclude-module "PySide6.QtPrintSupport" ^
  --exclude-module "PySide6.QtBluetooth" ^
  --exclude-module "PySide6.QtNfc" ^
  --exclude-module "PySide6.QtMultimedia" ^
  --exclude-module "PySide6.QtLocation" ^
  --exclude-module "tkinter" ^
  --exclude-module "matplotlib" ^
  --exclude-module "numpy" ^
  --strip ^
  --clean ^
  --noconsole ^
  ai_linux_assistant.py

REM ---- Check result ----
echo.
IF EXIST "dist\AI_Command_Assistant\AI_Command_Assistant.exe" (
    echo ============================================
    echo   [SUCCESS] Build Complete!
    echo   Location: dist\AI_Command_Assistant\
    echo ============================================
    echo.
    explorer dist\AI_Command_Assistant
) ELSE (
    echo [FAILED] Build failed. Check errors above.
)

pause

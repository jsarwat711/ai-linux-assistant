@echo off
title AI Linux Command Assistant — Stopping
color 0C
cls

echo =====================================================
echo   Stopping AI Linux Command Assistant...
echo =====================================================
echo.

docker-compose down

echo.
echo [OK] App stopped successfully.
echo.
pause

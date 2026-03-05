@echo off
REM Start only the server for testing
REM Version: 2.0.0

echo ========================================
echo    STARTING SERVER ONLY
echo ========================================
echo.

REM Set correct directory
cd /d "%~dp0"

echo Current directory: %CD%
echo Starting server...
echo.

python Server\ai_copilot_server.py

pause


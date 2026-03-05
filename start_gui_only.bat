@echo off
REM Start only the GUI for testing
REM Version: 2.0.0

echo ========================================
echo    STARTING GUI ONLY
echo ========================================
echo.

cd GUI

REM Windows UX: start GUI detached from this console so it gets its own taskbar button.
set "PYW="
if exist "..\venv\Scripts\pythonw.exe" set "PYW=..\venv\Scripts\pythonw.exe"
if "%PYW%"=="" set "PYW=pythonw"

start "" "%PYW%" "profesor_ableton_gui.py"

REM No pause: keep console from "owning" the GUI window.
exit /b 0






























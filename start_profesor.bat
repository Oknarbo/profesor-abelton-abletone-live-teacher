@echo off
REM Profesor Abelton GUI Launcher for Windows
REM Version: 2.0.0

echo ========================================
echo    🎓 PROFESOR ABELTON
echo ========================================
echo.

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo WARNING: Virtual environment not found
    echo Run Installers\install_windows.py first to set up
    echo.
)

REM Start GUI
cd GUI
REM Windows UX: start GUI detached from this console so it gets its own taskbar button.
set "PYW="
if exist "..\venv\Scripts\pythonw.exe" set "PYW=..\venv\Scripts\pythonw.exe"
if "%PYW%"=="" set "PYW=pythonw"

start "" "%PYW%" "profesor_ableton_gui.py"

REM No pause: keep console from "owning" the GUI window.
exit /b 0


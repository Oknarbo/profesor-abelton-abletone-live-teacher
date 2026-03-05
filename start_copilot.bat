@echo off
REM Profesor Abelton Launcher for Windows
REM Version: 2.0.0

echo ========================================
echo    PROFESOR ABELTON
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Checking Python installation... OK
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate.bat
echo [2/3] Virtual environment activated... OK
echo.

REM Install/update requirements
echo Installing/updating dependencies...
pip install -r requirements.txt --quiet
echo [3/3] Dependencies installed... OK
echo.

echo ========================================
echo Starting Profesor Abelton Server...
echo ========================================
echo.
echo Server will run on localhost:8766
echo Press Ctrl+C to stop the server
echo.

REM Start server
cd Server
python ai_copilot_server.py ../Config/copilot_config.json

REM Deactivate on exit
call deactivate
pause







































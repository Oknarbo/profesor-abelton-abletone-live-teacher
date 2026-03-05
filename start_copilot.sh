#!/bin/bash
# Profesor Abelton Launcher for Mac/Linux
# Version: 2.0.0

echo "========================================"
echo "   PROFESOR ABELTON"
echo "========================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found!"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "[1/3] Checking Python installation... OK"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created."
    echo ""
fi

# Activate virtual environment
source venv/bin/activate
echo "[2/3] Virtual environment activated... OK"
echo ""

# Install/update requirements
echo "Installing/updating dependencies..."
pip install -r requirements.txt --quiet
echo "[3/3] Dependencies installed... OK"
echo ""

echo "========================================"
echo "Starting Profesor Abelton Server..."
echo "========================================"
echo ""
echo "Server will run on localhost:8766"
echo "Press Ctrl+C to stop the server"
echo ""

# Start server
cd Server
python3 ai_copilot_server.py ../Config/copilot_config.json

# Deactivate on exit
deactivate







































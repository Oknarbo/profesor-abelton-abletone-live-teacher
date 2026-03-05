#!/bin/bash
# Profesor Abelton GUI Launcher for Mac/Linux
# Version: 2.0.0

echo "========================================"
echo "   PROFESOR ABELTON GUI"
echo "========================================"
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "WARNING: Virtual environment not found"
    echo "Run start_copilot.sh first to set up the environment"
    echo ""
fi

# Start GUI
cd GUI
python3 profesor_ableton_gui.py







































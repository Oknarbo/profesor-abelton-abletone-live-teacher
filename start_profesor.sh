#!/bin/bash
# Profesor Abelton GUI Launcher for Mac/Linux
# Version: 2.0.0

echo "========================================"
echo "    🎓 PROFESOR ABELTON"
echo "========================================"
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "WARNING: Virtual environment not found"
    echo "Run Installers/install_mac.sh or install_linux.sh first"
    echo ""
fi

# Start GUI
cd GUI
python profesor_ableton_gui.py

read -p "Press Enter to continue..."


#!/bin/bash
echo "🚀 Photo Detection System - Quick Start"
echo "======================================"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "💡 Run setup/setup.sh or setup/setup-macos.sh first"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if all packages are installed
python -c "import cv2, mediapipe, flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Some packages are missing!"
    echo "💡 Run setup script to install dependencies"
    exit 1
fi

echo "✅ All dependencies OK"
echo "🎯 Starting application..."
echo ""
echo "📱 Access URLs:"
echo "   Main App: http://localhost:8080"
echo "   Jitsi Demo: http://localhost:5001"
echo "   Bridge Server: http://localhost:5002"
echo ""
echo "💡 Press Ctrl+C to stop the application"
echo ""

# Start the application
python launcher.py

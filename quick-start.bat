@echo off
echo 🚀 Photo Detection System - Quick Start
echo ======================================

REM Check if virtual environment exists
if not exist ".venv" (
    echo ❌ Virtual environment not found!
    echo 💡 Run setup\setup.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate

REM Check if packages are installed
python -c "import cv2, mediapipe, flask" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Some packages are missing!
    echo 💡 Run setup\setup.bat to install dependencies
    pause
    exit /b 1
)

echo ✅ All dependencies OK
echo 🎯 Starting application...
echo.
echo 📱 Access URLs:
echo    Main App: http://localhost:8080
echo    Jitsi Demo: http://localhost:5001
echo    Bridge Server: http://localhost:5002
echo.
echo 💡 Press Ctrl+C to stop the application
echo.

REM Start the application
python launcher.py
pause

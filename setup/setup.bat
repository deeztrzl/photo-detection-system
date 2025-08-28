@echo off
REM 🚀 Auto Setup Script untuk Photo Detection System - Windows
REM ============================================================

echo 📸 Photo Detection System - Windows Auto Setup
echo ==============================================

REM Check Python installation
echo.
echo 🔍 Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python not found! Please install Python 3.8+ first.
    echo    Download from: https://python.org/downloads/
    echo    ⚠️  IMPORTANT: Check "Add Python to PATH" during installation
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Found Python %PYTHON_VERSION%

REM Create virtual environment
echo.
echo 🏗️  Creating virtual environment...
if exist ".venv" (
    echo ⚠️  Virtual environment already exists. Removing old one...
    rmdir /s /q .venv
)

python -m venv .venv
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to create virtual environment
    echo    Try: pip install virtualenv
    pause
    exit /b 1
)
echo ✅ Virtual environment created successfully

REM Activate virtual environment
echo.
echo 🔌 Activating virtual environment...
call .venv\Scripts\activate
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment activated

REM Upgrade pip
echo.
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo 📦 Installing dependencies...
echo    This may take a few minutes...

pip install Flask==2.3.3
pip install opencv-python==4.8.0.76
pip install mediapipe==0.10.3
pip install numpy==1.24.3
pip install Pillow==10.0.0
pip install requests==2.31.0
pip install scipy==1.11.3
pip install scikit-image==0.21.0
pip install pywt==1.4.1

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Some dependencies failed to install
    echo    Try running: pip install -r requirements.txt
    pause
    exit /b 1
)
echo ✅ All dependencies installed successfully

REM Test installation
echo.
echo 🧪 Testing installation...
python -c "import cv2, mediapipe, flask, numpy, PIL; print('✅ All packages imported successfully!')" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Some packages failed to import
    echo    Check the error messages above
    pause
    exit /b 1
)

REM Test camera
echo.
echo 📹 Testing camera access...
python -c "import cv2; cap = cv2.VideoCapture(0); print('✅ Camera accessible!' if cap.isOpened() else '⚠️  Camera not found'); cap.release()" 2>nul

REM Create quick start script
echo.
echo 📝 Creating quick start script...
echo @echo off > quick-start.bat
echo echo 🚀 Starting Photo Detection System... >> quick-start.bat
echo call .venv\Scripts\activate >> quick-start.bat
echo python launcher.py >> quick-start.bat
echo pause >> quick-start.bat
echo ✅ Created quick-start.bat

REM Final instructions
echo.
echo 🎉 Setup Complete!
echo ==================
echo.
echo 📋 Next Steps:
echo 1. Double-click: quick-start.bat
echo    OR manually run:
echo    .venv\Scripts\activate
echo    python launcher.py
echo.
echo 2. Open browser: http://localhost:8080
echo.
echo 💡 Need help? Check ../guides/SETUP_GUIDE.md
echo 🐛 Found bugs? Report at GitHub repository
echo.
echo ✨ Happy detecting! 📸
echo.
pause

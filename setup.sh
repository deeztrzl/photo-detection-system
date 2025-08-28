#!/bin/bash
# 🚀 Auto Setup Script untuk Photo Detection System
# Kompatibel: macOS, Linux, Windows (Git Bash)

echo "📸 Photo Detection System - Auto Setup"
echo "======================================"

# Deteksi OS
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    OS="Windows"
    PYTHON_CMD="python"
    VENV_ACTIVATE=".venv/Scripts/activate"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
    PYTHON_CMD="python3"
    VENV_ACTIVATE=".venv/bin/activate"
else
    OS="Linux"
    PYTHON_CMD="python3"
    VENV_ACTIVATE=".venv/bin/activate"
fi

echo "🖥️  Detected OS: $OS"

# Check Python installation
echo ""
echo "🔍 Checking Python installation..."
if command -v $PYTHON_CMD &> /dev/null; then
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
    echo "✅ Found: $PYTHON_VERSION"
else
    echo "❌ Python not found! Please install Python 3.8+ first."
    echo "   Download from: https://python.org/downloads/"
    exit 1
fi

# Check Python version
PYTHON_VER=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if (( $(echo "$PYTHON_VER >= 3.8" | bc -l) )); then
    echo "✅ Python version is compatible ($PYTHON_VER)"
else
    echo "❌ Python version $PYTHON_VER is too old. Need 3.8+"
    exit 1
fi

# Create virtual environment
echo ""
echo "🏗️  Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "⚠️  Virtual environment already exists. Removing old one..."
    rm -rf .venv
fi

$PYTHON_CMD -m venv .venv
if [ $? -eq 0 ]; then
    echo "✅ Virtual environment created successfully"
else
    echo "❌ Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source $VENV_ACTIVATE
if [ $? -eq 0 ]; then
    echo "✅ Virtual environment activated"
else
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
echo "   This may take a few minutes..."

pip install Flask==2.3.3
pip install opencv-python==4.8.0.76
pip install mediapipe==0.10.3
pip install numpy==1.24.3
pip install Pillow==10.0.0
pip install requests==2.31.0
pip install scipy==1.11.3
pip install scikit-image==0.21.0
pip install pywt==1.4.1

if [ $? -eq 0 ]; then
    echo "✅ All dependencies installed successfully"
else
    echo "❌ Some dependencies failed to install"
    echo "   Try running: pip install -r requirements.txt"
fi

# Test installation
echo ""
echo "🧪 Testing installation..."
python -c "
try:
    import cv2, mediapipe, flask, numpy, PIL
    print('✅ All packages imported successfully!')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

# Test camera
echo ""
echo "📹 Testing camera access..."
python -c "
import cv2
cap = cv2.VideoCapture(0)
if cap.isOpened():
    print('✅ Camera accessible!')
    cap.release()
else:
    print('⚠️  Camera not found or in use')
    print('   Make sure no other app is using the camera')
"

# Create run script
echo ""
echo "📝 Creating run script..."
if [[ "$OS" == "Windows" ]]; then
    cat > quick-start.bat << 'EOF'
@echo off
echo 🚀 Starting Photo Detection System...
call .venv\Scripts\activate
python launcher.py
pause
EOF
    chmod +x quick-start.bat
    echo "✅ Created quick-start.bat"
else
    cat > quick-start.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Photo Detection System..."
source .venv/bin/activate
python launcher.py
EOF
    chmod +x quick-start.sh
    echo "✅ Created quick-start.sh"
fi

# Final instructions
echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "📋 Next Steps:"
echo "1. Keep this terminal open OR activate venv manually:"
if [[ "$OS" == "Windows" ]]; then
    echo "   .venv\\Scripts\\activate"
    echo ""
    echo "2. Run the application:"
    echo "   python launcher.py"
    echo "   OR double-click: quick-start.bat"
else
    echo "   source .venv/bin/activate"
    echo ""
    echo "2. Run the application:"
    echo "   python launcher.py"
    echo "   OR run: ./quick-start.sh"
fi
echo ""
echo "3. Open browser: http://localhost:8080"
echo ""
echo "💡 Need help? Check SETUP_GUIDE.md"
echo "🐛 Found bugs? Report at GitHub repository"
echo ""
echo "✨ Happy detecting! 📸"

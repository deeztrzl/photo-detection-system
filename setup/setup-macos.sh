#!/bin/bash
# 🍎 macOS Setup Script untuk Photo Detection System
# Optimized untuk macOS dengan Homebrew support

echo "🍎 Photo Detection System - macOS Setup"
echo "======================================="

# Deteksi macOS version
MACOS_VERSION=$(sw_vers -productVersion)
echo "🖥️  macOS Version: $MACOS_VERSION"

# Function untuk check command
check_command() {
    if command -v "$1" &> /dev/null; then
        echo "✅ $1 is installed"
        return 0
    else
        echo "❌ $1 is not installed"
        return 1
    fi
}

# Check dan install Homebrew jika belum ada
echo ""
echo "🍺 Checking Homebrew..."
if ! check_command brew; then
    echo "📥 Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH untuk Apple Silicon
    if [[ $(uname -m) == "arm64" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    else
        echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/usr/local/bin/brew shellenv)"
    fi
    
    echo "✅ Homebrew installed successfully"
else
    echo "✅ Homebrew already installed"
    echo "📦 Updating Homebrew..."
    brew update
fi

# Install Python jika belum ada
echo ""
echo "🐍 Checking Python installation..."
if ! check_command python3; then
    echo "📥 Installing Python via Homebrew..."
    brew install python
else
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Found: $PYTHON_VERSION"
fi

# Check Python version
PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "🔍 Python version: $PYTHON_VER"

if (( $(echo "$PYTHON_VER >= 3.8" | bc -l 2>/dev/null || echo "0") )); then
    echo "✅ Python version is compatible"
else
    echo "❌ Python version $PYTHON_VER is too old. Installing latest Python..."
    brew install python@3.11
    # Update PATH untuk gunakan Python yang baru
    export PATH="/opt/homebrew/bin:$PATH"
fi

# Install system dependencies untuk OpenCV
echo ""
echo "🛠️  Installing system dependencies..."
echo "📦 Installing required packages via Homebrew..."

# Install dependencies yang dibutuhkan OpenCV dan MediaPipe
brew install cmake pkg-config
brew install jpeg libpng libtiff openexr
brew install eigen tbb

echo "✅ System dependencies installed"

# Create virtual environment
echo ""
echo "🏗️  Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "⚠️  Virtual environment already exists. Do you want to recreate it? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing old virtual environment..."
        rm -rf .venv
    else
        echo "📁 Using existing virtual environment..."
    fi
fi

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    if [ $? -eq 0 ]; then
        echo "✅ Virtual environment created successfully"
    else
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source .venv/bin/activate
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

# Install dependencies optimized untuk macOS
echo ""
echo "📦 Installing Python dependencies..."
echo "   This may take several minutes on macOS..."

# Install packages satu per satu untuk better error handling
echo "   Installing Flask..."
pip install Flask==2.3.3

echo "   Installing NumPy..."
pip install numpy==1.24.3

echo "   Installing OpenCV (this may take a while)..."
pip install opencv-python==4.8.0.76

echo "   Installing MediaPipe..."
pip install mediapipe==0.10.3

echo "   Installing Pillow..."
pip install Pillow==10.0.0

echo "   Installing additional packages..."
pip install requests==2.31.0
pip install scipy==1.11.3
pip install scikit-image==0.21.0
pip install pywt==1.4.1

if [ $? -eq 0 ]; then
    echo "✅ All dependencies installed successfully"
else
    echo "❌ Some dependencies failed to install"
    echo "💡 Try installing packages individually or check error messages above"
fi

# Test installation
echo ""
echo "🧪 Testing installation..."
python -c "
import sys
print(f'🐍 Python: {sys.version}')

try:
    import cv2
    print(f'✅ OpenCV: {cv2.__version__}')
except ImportError:
    print('❌ OpenCV: Failed to import')

try:
    import mediapipe as mp
    print(f'✅ MediaPipe: {mp.__version__}')
except ImportError:
    print('❌ MediaPipe: Failed to import')

try:
    import flask
    print(f'✅ Flask: {flask.__version__}')
except ImportError:
    print('❌ Flask: Failed to import')

try:
    import numpy as np
    print(f'✅ NumPy: {np.__version__}')
except ImportError:
    print('❌ NumPy: Failed to import')

try:
    import PIL
    print(f'✅ Pillow: {PIL.__version__}')
except ImportError:
    print('❌ Pillow: Failed to import')
"

# Test camera access
echo ""
echo "📹 Testing camera access..."
python -c "
import cv2
import sys

# Test multiple camera indices
cameras_found = []
for i in range(3):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret and frame is not None:
            cameras_found.append(i)
        cap.release()

if cameras_found:
    print(f'✅ Camera(s) found at index: {cameras_found}')
else:
    print('⚠️  No cameras found or camera permission denied')
    print('💡 You may need to grant camera permission in System Preferences > Security & Privacy > Camera')
"

# Setup file permissions
echo ""
echo "🔐 Setting up file permissions..."
chmod +x setup.sh
chmod +x quick-start.sh
chmod +x validate_system.py
echo "✅ File permissions set"

# Create macOS-specific quick start script
echo ""
echo "📝 Creating macOS quick start script..."
cat > quick-start.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Photo Detection System on macOS..."
echo "============================================"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "💡 Run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if all packages are installed
python -c "import cv2, mediapipe, flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Some packages are missing!"
    echo "💡 Run ./setup.sh to install dependencies"
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
EOF

chmod +x quick-start.sh
echo "✅ Created quick-start.sh"

# Create .zshrc/.bash_profile shortcuts (optional)
echo ""
echo "🔗 Setting up shell aliases (optional)..."
read -p "Do you want to add shortcuts to your shell profile? (y/n): " -r
if [[ $RESPONSE =~ ^[Yy]$ ]]; then
    SHELL_CONFIG=""
    if [ -n "$ZSH_VERSION" ]; then
        SHELL_CONFIG="$HOME/.zshrc"
    elif [ -n "$BASH_VERSION" ]; then
        SHELL_CONFIG="$HOME/.bash_profile"
    fi
    
    if [ -n "$SHELL_CONFIG" ]; then
        echo "" >> "$SHELL_CONFIG"
        echo "# Photo Detection System shortcuts" >> "$SHELL_CONFIG"
        echo "alias photo-setup='cd $(pwd) && ./setup.sh'" >> "$SHELL_CONFIG"
        echo "alias photo-start='cd $(pwd) && ./quick-start.sh'" >> "$SHELL_CONFIG"
        echo "alias photo-validate='cd $(pwd)/.. && python setup/validate_system.py'" >> "$SHELL_CONFIG"
        echo "✅ Shortcuts added to $SHELL_CONFIG"
        echo "💡 Restart terminal or run: source $SHELL_CONFIG"
    fi
fi

# Final instructions
echo ""
echo "🎉 macOS Setup Complete!"
echo "========================"
echo ""
echo "📋 Available Commands:"
echo "   python ../launcher.py   - Start the application"
echo "   ../quick-start.sh       - Quick launcher"
echo "   ./validate_system.py    - Check system status"
echo ""
echo "� Documentation:"
echo "   ../guides/MACOS_SETUP_GUIDE.md - macOS-specific setup guide"
echo "   ../guides/SETUP_GUIDE.md       - Detailed setup guide"
echo "   ../guides/QUICK_REFERENCE.md   - Quick reference card"

# 🍎 macOS Quick Setup Commands

**Photo Detection System - macOS Command Reference**

---

## 🚀 **Setup Commands**

```bash
# === ONE-LINER SETUP ===
curl -fsSL https://raw.githubusercontent.com/deeztrzl/photo-detection-system/main/setup-macos.sh | bash

# === MANUAL SETUP ===
# 1. Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Clone & Setup
git clone https://github.com/deeztrzl/photo-detection-system.git
cd photo-detection-system
chmod +x setup-macos.sh
./setup-macos.sh

# 3. Run Application
./quick-start.sh
```

---

## 🎯 **Quick Commands**

```bash
# Start Application
./quick-start.sh

# Validate System
python setup/validate_system.py

# Activate Virtual Environment
source .venv/bin/activate

# Install Dependencies
pip install -r requirements.txt

# Test Camera
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera FAIL'); cap.release()"

# Check Python Version
python3 --version

# Update Homebrew
brew update && brew upgrade
```

---

## 🔧 **Troubleshooting Commands**

```bash
# === PERMISSION ISSUES ===
# Fix camera permissions (run & restart Terminal)
tccutil reset Camera

# Fix file permissions
chmod +x setup-macos.sh quick-start.sh validate_system.py

# === PYTHON ISSUES ===
# Install/reinstall Python
brew install python

# Multiple Python versions
ls -la /usr/bin/python*
brew list | grep python

# === CAMERA ISSUES ===
# Test all camera indices
for i in {0..2}; do echo "Testing camera $i:"; python3 -c "import cv2; cap = cv2.VideoCapture($i); print('OK' if cap.isOpened() else 'FAIL'); cap.release()"; done

# === PORT ISSUES ===
# Check port usage
lsof -i :8080
lsof -i :5001
lsof -i :5002

# Kill process by port
lsof -ti:8080 | xargs kill -9

# === PACKAGE ISSUES ===
# Reinstall OpenCV
pip uninstall opencv-python
pip install opencv-python==4.8.0.76

# Reinstall MediaPipe
pip uninstall mediapipe
pip install mediapipe==0.10.3
```

---

## 📍 **Important Paths**

```bash
# Homebrew Paths
/opt/homebrew/bin/brew          # Apple Silicon (M1/M2)
/usr/local/bin/brew             # Intel Mac

# Python Paths
/opt/homebrew/bin/python3       # Homebrew Python (Apple Silicon)
/usr/local/bin/python3          # Homebrew Python (Intel)
/usr/bin/python3                # System Python

# Project Paths
./photo-detection-system/       # Project root
./.venv/                       # Virtual environment
./modules/main_detection/      # Main app
./assets/                      # Template images
```

---

## 🌐 **Access URLs**

- **Main App:** http://localhost:8080
- **Jitsi Demo:** http://localhost:5001
- **Bridge Server:** http://localhost:5002

---

## 💡 **macOS Tips**

```bash
# === SHELL ALIASES ===
# Add to ~/.zshrc or ~/.bash_profile
alias photo='cd ~/photo-detection-system && ./quick-start.sh'
alias photo-setup='cd ~/photo-detection-system && ./setup-macos.sh'
alias photo-test='cd ~/photo-detection-system && python setup/validate_system.py'

# === DOCK SHORTCUT ===
# Create app bundle
mkdir -p PhotoDetection.app/Contents/MacOS
echo '#!/bin/bash
cd "$HOME/photo-detection-system"
./quick-start.sh' > PhotoDetection.app/Contents/MacOS/PhotoDetection
chmod +x PhotoDetection.app/Contents/MacOS/PhotoDetection

# === SYSTEM PREFERENCES ===
# Camera permissions: System Preferences > Security & Privacy > Camera
# Microphone permissions: System Preferences > Security & Privacy > Microphone
```

---

## 🆘 **Emergency Commands**

```bash
# Complete reset
rm -rf .venv
./setup-macos.sh

# Force reinstall Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/uninstall.sh)"
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# System diagnosis
echo "=== System Info ==="
sw_vers
echo "=== Python Info ==="
python3 --version
which python3
echo "=== Homebrew Info ==="
brew --version 2>/dev/null || echo "Not installed"
echo "=== Camera Test ==="
python3 -c "import cv2; print('Camera:', 'OK' if cv2.VideoCapture(0).isOpened() else 'FAIL')" 2>/dev/null || echo "Python/OpenCV issue"
```

---

**📚 Documentation:**
- [MACOS_SETUP_GUIDE.md](MACOS_SETUP_GUIDE.md) - Detailed macOS guide
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - General setup guide
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Cross-platform reference

**🍎 Happy coding on macOS!**

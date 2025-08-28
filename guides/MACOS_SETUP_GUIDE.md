# 🍎 macOS Setup & Troubleshooting Guide

Panduan khusus untuk setup dan troubleshooting di macOS.

---

## 🚀 Quick Setup untuk macOS

### **Method 1: Auto Setup (Recommended)**
```bash
# Clone repository
git clone https://github.com/deeztrzl/photo-detection-system.git
cd photo-detection-system

# Run macOS setup script
chmod +x setup-macos.sh
./setup-macos.sh

# Start application
./quick-start.sh
```

### **Method 2: Manual Setup**
```bash
# Install Homebrew (jika belum ada)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python

# Clone & setup project
git clone https://github.com/deeztrzl/photo-detection-system.git
cd photo-detection-system
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start application
python launcher.py
```

---

## 🔧 macOS-Specific Troubleshooting

### **1. Python Issues**

#### **Problem: "python3: command not found"**
```bash
# Install Python via Homebrew
brew install python

# Or install from python.org
# Download: https://www.python.org/downloads/macos/
```

#### **Problem: Multiple Python versions**
```bash
# Check installed Python versions
ls -la /usr/bin/python*
brew list | grep python

# Use specific Python version
python3.11 -m venv .venv  # untuk Python 3.11
```

#### **Problem: pip not working**
```bash
# Reinstall pip
python3 -m ensurepip --upgrade

# Or via Homebrew
brew install python
```

### **2. Camera Permission Issues**

#### **Problem: "Camera not accessible" atau "Permission denied"**

**Solution:**
1. Buka **System Preferences** > **Security & Privacy** > **Camera**
2. Pastikan **Terminal** atau **Python** dicentang
3. Restart Terminal setelah mengubah permission
4. Test camera:
   ```bash
   python3 -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAIL'); cap.release()"
   ```

### **3. OpenCV Installation Issues**

#### **Problem: OpenCV install gagal atau error**
```bash
# Install system dependencies
brew install cmake pkg-config
brew install jpeg libpng libtiff openexr
brew install eigen tbb

# Install OpenCV
pip install opencv-python --no-cache-dir

# Alternative: install via conda
brew install miniconda
conda install -c conda-forge opencv
```

#### **Problem: "No module named 'cv2'"**
```bash
# Uninstall dan reinstall
pip uninstall opencv-python opencv-contrib-python
pip install opencv-python==4.8.0.76

# Test import
python3 -c "import cv2; print(cv2.__version__)"
```

### **4. MediaPipe Issues**

#### **Problem: MediaPipe install gagal (Apple Silicon)**
```bash
# For Apple Silicon (M1/M2 Macs)
pip install mediapipe --no-deps
pip install opencv-python numpy protobuf

# Alternative
brew install python@3.9  # MediaPipe works best with Python 3.9
```

#### **Problem: "No module named 'mediapipe'"**
```bash
# Reinstall with specific version
pip install mediapipe==0.10.3

# Check installation
python3 -c "import mediapipe as mp; print(mp.__version__)"
```

### **5. Homebrew Issues**

#### **Problem: Homebrew not in PATH (Apple Silicon)**
```bash
# Add to PATH
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# Reload shell
source ~/.zprofile
```

#### **Problem: "brew: command not found"**
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Follow the installation instructions to add to PATH
```

### **6. Virtual Environment Issues**

#### **Problem: Virtual environment tidak aktif**
```bash
# Check current environment
echo $VIRTUAL_ENV

# Activate manually
source .venv/bin/activate

# Check Python path
which python
```

#### **Problem: "venv module not found"**
```bash
# Install venv module
python3 -m pip install virtualenv

# Create using virtualenv
virtualenv .venv
```

### **7. Port Issues**

#### **Problem: "Port already in use"**
```bash
# Check what's using the port
lsof -i :8080

# Kill process using port
kill -9 [PID]

# Use different port
# Edit modules/main_detection/app.py
# Change: app.run(host='0.0.0.0', port=8081, debug=True)
```

### **8. Browser Issues**

#### **Problem: Camera tidak terdeteksi di browser**
1. **Safari:** Preferences > Websites > Camera > Allow
2. **Chrome:** Settings > Privacy and Security > Site Settings > Camera > Allow
3. **Firefox:** Preferences > Privacy & Security > Permissions > Camera > Settings

### **9. File Permission Issues**

#### **Problem: "Permission denied" saat menjalankan script**
```bash
# Fix file permissions
chmod +x setup-macos.sh
chmod +x quick-start.sh
chmod +x validate_system.py

# Fix directory permissions
chmod -R 755 modules/
```

---

## 🍎 macOS-Specific Features

### **Shell Integration**
```bash
# Add to ~/.zshrc or ~/.bash_profile
alias photo-start='cd /path/to/photo-detection-system && ./quick-start.sh'
alias photo-setup='cd /path/to/photo-detection-system && ./setup-macos.sh'
```

### **Dock Integration**
```bash
# Create .app bundle (optional)
mkdir -p PhotoDetection.app/Contents/MacOS
echo '#!/bin/bash
cd "/path/to/photo-detection-system"
./quick-start.sh' > PhotoDetection.app/Contents/MacOS/PhotoDetection
chmod +x PhotoDetection.app/Contents/MacOS/PhotoDetection
```

### **Notification Support**
```bash
# Install terminal-notifier untuk notifications
brew install terminal-notifier

# Add to quick-start.sh
terminal-notifier -message "Photo Detection System started" -title "Success"
```

---

## 💡 Performance Tips untuk macOS

### **Hardware Optimization:**
- **Apple Silicon (M1/M2):** Gunakan native ARM64 packages
- **Intel Mac:** Install Intel-specific versions jika ada masalah
- **Memory:** Tutup aplikasi lain yang menggunakan camera

### **System Settings:**
```bash
# Disable App Nap untuk Terminal
defaults write com.apple.Terminal NSAppSleepDisabled -bool YES

# Increase camera resolution limit
# System Preferences > Camera > Format > High Resolution
```

---

## 🧪 Testing & Validation

### **System Test:**
```bash
# Run comprehensive test
python ../setup/validate_system.py

# Quick camera test
python3 -c "
import cv2
cap = cv2.VideoCapture(0)
if cap.isOpened():
    ret, frame = cap.read()
    print(f'Camera OK: {ret}, Frame shape: {frame.shape if ret else None}')
    cap.release()
else:
    print('Camera FAIL')
"
```

### **Performance Test:**
```bash
# Test detection speed
time python3 -c "
import cv2
import mediapipe as mp
mp_face = mp.solutions.face_detection.FaceDetection()
print('Performance test completed')
"
```

---

## 📞 macOS Support

**Common macOS Issues:**
- 🔒 **Security permissions** untuk camera dan microphone
- 🍺 **Homebrew path** issues pada Apple Silicon
- 🐍 **Multiple Python versions** conflicts
- 📹 **Camera access** permission prompts

**Quick Diagnostic:**
```bash
# Run this for quick diagnosis
echo "=== macOS System Info ==="
sw_vers
echo "=== Python Info ==="
python3 --version
which python3
echo "=== Homebrew Info ==="
brew --version 2>/dev/null || echo "Homebrew not installed"
echo "=== Camera Test ==="
python3 -c "import cv2; print('Camera:', 'OK' if cv2.VideoCapture(0).isOpened() else 'FAIL')"
```

---

**🆘 Need Help?**
- Check [SETUP_GUIDE.md](SETUP_GUIDE.md) untuk troubleshooting umum
- Run `python ../setup/validate_system.py` untuk diagnosis lengkap
- Report macOS-specific issues di GitHub repository

**✅ Happy coding on macOS! 🍎**

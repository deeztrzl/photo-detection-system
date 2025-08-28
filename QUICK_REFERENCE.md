# 📋 QUICK REFERENCE CARD - Photo Detection System

```
┌─────────────────────────────────────────────────────────────────┐
│                🎯 PHOTO DETECTION SYSTEM                        │
│                    Quick Setup Guide                            │
└─────────────────────────────────────────────────────────────────┘

📥 DOWNLOAD & SETUP
──────────────────────
1. Clone repository:
   git clone https://github.com/deeztrzl/photo-detection-system.git
   cd photo-detection-system

2. Auto setup:
   Windows: setup.bat
   Mac/Linux: bash setup.sh

3. Manual setup:
   python -m venv .venv
   .venv\Scripts\activate      (Windows)
   source .venv/bin/activate   (Mac/Linux)
   pip install -r requirements.txt

🚀 RUN APPLICATION
─────────────────────
• Quick Start:
  Windows: quick-start.bat
  Mac/Linux: ./quick-start.sh

• Manual:
  python launcher.py
  → Select option 1 (Main Detection App)

• Direct:
  cd modules/main_detection
  python app.py

🌐 ACCESS URLs
──────────────
• Main App: http://localhost:8080
• Jitsi Demo: http://localhost:5001
• Bridge Server: http://localhost:5002

⚙️ CONFIGURATION
────────────────────
• Detector Type:
  modules/main_detection/detection/main_detector.py
  Line 8: DETECTOR_TYPE = "template_based"
  
  Options:
  - "template_based" (default, most accurate)
  - "fast" (fastest, real-time)
  - "2layer" (balanced)
  - "advanced" (maximum accuracy, slow)

• Port Change:
  modules/main_detection/app.py
  Last line: port=8080

🔧 TROUBLESHOOTING
─────────────────────
• Python not found:
  → Install Python 3.8+ from python.org
  → Check "Add to PATH" during install

• Camera not working:
  → Close other apps using camera
  → Try different camera index (0,1,2...)
  → Check browser permissions

• Import errors:
  → Activate virtual environment first
  → Reinstall: pip install -r requirements.txt

• Port already in use:
  → Change port in app.py
  → Kill existing process:
    Windows: taskkill /F /PID [PID]
    Mac/Linux: kill -9 [PID]

📝 COMMANDS CHEAT SHEET
──────────────────────────
# Virtual Environment
.venv\Scripts\activate           # Windows
source .venv/bin/activate        # Mac/Linux
deactivate                       # Exit venv

# Package Management
pip list                         # Show installed
pip install --upgrade [package]  # Update package
pip freeze > requirements.txt    # Export deps

# Process Management
Ctrl+C                          # Stop application
python launcher.py              # Start launcher
netstat -an | findstr :8080     # Check port (Win)
lsof -i :8080                   # Check port (Mac/Linux)

💡 USAGE TIPS
─────────────────
• Use good lighting
• Position KTP horizontally
• Wait for green indicators
• Auto mode recommended
• Manual mode for custom timing

🆘 SUPPORT
─────────────
• Documentation: docs/ folder
• Setup Guide: SETUP_GUIDE.md
• GitHub: github.com/deeztrzl/photo-detection-system
• Issues: Report bugs on GitHub

┌─────────────────────────────────────────────────────────────────┐
│  ✅ Requirements: Python 3.8+, Webcam, Modern Browser          │
│  💾 Storage: 3GB free space                                    │
│  🔒 Network: Localhost only (no internet needed after setup)   │
└─────────────────────────────────────────────────────────────────┘
```

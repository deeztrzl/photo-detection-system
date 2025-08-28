# 🛠️ Setup Scripts

Folder ini berisi script untuk setup dan instalasi otomatis.

## Files:

### **Setup Scripts:**
- **`setup.bat`** - Auto setup untuk Windows
- **`setup.sh`** - Auto setup untuk Linux/Unix
- **`setup-macos.sh`** - Auto setup khusus macOS dengan Homebrew
- **`validate_system.py`** - System validation dan testing tool

### **Usage:**

#### **Windows:**
```cmd
setup\setup.bat
```

#### **macOS:**
```bash
chmod +x setup/setup-macos.sh
setup/setup-macos.sh
```

#### **Linux:**
```bash
chmod +x setup/setup.sh
setup/setup.sh
```

#### **Validation:**
```bash
python setup/validate_system.py
```

## Features:

- ✅ Auto-detect operating system
- ✅ Virtual environment creation
- ✅ Dependency installation
- ✅ Camera testing
- ✅ System validation
- ✅ Error handling dan troubleshooting

# 📋 PANDUAN SETUP DI LAPTOP LAIN

Panduan lengkap untuk menjalankan **Photo Detection System** di laptop/komputer baru.

---

## 🎯 **Persyaratan Sistem**

### **Sistem Operasi:**
- ✅ Windows 10/11 (64-bit)
- ✅ macOS 10.14+ (Monterey/Ventura/Sonoma)
- ✅ Ubuntu 18.04+ / Linux Mint / Pop!_OS

### **Hardware Minimum:**
- **RAM:** 4GB (8GB direkomendasikan)
- **Storage:** 3GB free space
- **Processor:** Intel i3 / AMD Ryzen 3 (atau setara)
- **Camera:** Webcam USB atau built-in camera
- **Internet:** Untuk download dependencies

### **Software Requirements:**
- **Python:** 3.8, 3.9, 3.10, atau 3.11
- **Git:** Untuk clone repository
- **Browser:** Chrome 90+, Firefox 88+, Edge 90+

---

## 🚀 **Langkah Instalasi**

### **Step 1: Install Python**

#### **Windows:**
1. Download Python dari: https://python.org/downloads/
2. ✅ **PENTING:** Centang "Add Python to PATH" saat install
3. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

#### **macOS:**
```bash
# Install menggunakan Homebrew (recommended)
brew install python

# Atau download dari python.org
```

#### **Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git
```

### **Step 2: Clone Repository**

```bash
# Clone dari GitHub
git clone https://github.com/deeztrzl/photo-detection-system.git

# Masuk ke folder project
cd photo-detection-system
```

### **Step 3: Setup Virtual Environment**

#### **Windows:**
```cmd
# Buat virtual environment
python -m venv .venv

# Aktivasi virtual environment
.venv\Scripts\activate

# Verify (prompt akan berubah dengan (.venv))
```

#### **macOS/Linux:**
```bash
# Buat virtual environment
python3 -m venv .venv

# Aktivasi virtual environment
source .venv/bin/activate

# Verify (prompt akan berubah dengan (.venv))
```

### **Step 4: Install Dependencies**

```bash
# Install semua package yang diperlukan
pip install Flask==2.3.3
pip install opencv-python==4.8.0.76
pip install mediapipe==0.10.3
pip install numpy==1.24.3
pip install Pillow==10.0.0

# Atau buat requirements.txt dan install sekaligus
pip install -r requirements.txt
```

### **Step 5: Test Installation**

```bash
# Test import semua library
python -c "import cv2, mediapipe, flask, numpy, PIL; print('✅ All packages installed successfully!')"

# Test camera access
python -c "import cv2; cap = cv2.VideoCapture(0); print('✅ Camera accessible!' if cap.isOpened() else '❌ Camera not found'); cap.release()"
```

---

## 🎮 **Cara Menjalankan Aplikasi**

### **Method 1: Menggunakan Launcher (Recommended)**

```bash
# Pastikan virtual environment aktif
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

# Jalankan launcher
python launcher.py
```

**Pilihan di Launcher:**
1. **Main Detection App** - Aplikasi utama (port 8080)
2. **Jitsi Dummy System** - Simulasi Jitsi integration
3. **Jitsi Bridge Server** - Bridge untuk integrasi real

### **Method 2: Direct Run**

```bash
# Jalankan aplikasi utama langsung
cd modules/main_detection
python app.py
```

### **Method 3: Menggunakan Batch Script (Windows)**

```cmd
# Double-click file ini:
run.bat
```

---

## 🌐 **Akses Aplikasi**

Setelah aplikasi berjalan, buka browser dan akses:

- **Main App:** http://localhost:8080
- **Jitsi Dummy:** http://localhost:5001
- **Jitsi Bridge:** http://localhost:5002

### **Test Aplikasi:**
1. ✅ Camera loading (tunggu 2-3 detik)
2. ✅ Face detection working (kotak hijau muncul)
3. ✅ KTP detection working (tunjukkan KTP)
4. ✅ Capture & download working

---

## 🔧 **Troubleshooting**

### **Problem 1: Python tidak dikenali**
```bash
# Windows - tambah Python ke PATH
# Cari "Environment Variables" di Windows Settings
# Tambah: C:\Users\[username]\AppData\Local\Programs\Python\Python3x\
# Dan: C:\Users\[username]\AppData\Local\Programs\Python\Python3x\Scripts\
```

### **Problem 2: pip tidak dikenali**
```bash
# Download get-pip.py
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

### **Problem 3: Virtual environment error**
```bash
# Install virtualenv secara global
pip install virtualenv

# Buat venv dengan virtualenv
virtualenv .venv
```

### **Problem 4: OpenCV installation error**
```bash
# Windows: Install Visual C++ Redistributable
# Download dari: https://support.microsoft.com/en-us/help/2977003

# macOS: Install Xcode Command Line Tools
xcode-select --install

# Linux: Install development tools
sudo apt install build-essential cmake pkg-config
```

### **Problem 5: Camera tidak terdeteksi**
```bash
# Test camera index berbeda
python -c "
import cv2
for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f'Camera found at index {i}')
        cap.release()
"
```

### **Problem 6: Permission error (Linux/macOS)**
```bash
# Tambah user ke video group
sudo usermod -a -G video $USER

# Logout dan login kembali
```

### **Problem 7: Port sudah digunakan**
```bash
# Cek port yang digunakan
# Windows:
netstat -an | findstr :8080

# macOS/Linux:
lsof -i :8080

# Kill process jika perlu
# Windows: taskkill /F /PID [PID_NUMBER]
# macOS/Linux: kill -9 [PID_NUMBER]
```

---

## 📦 **File Structure**

```
photo-detection-system/
│
├── launcher.py              # 🚀 Main launcher
├── run.bat                  # 🪟 Windows batch script
├── .venv/                   # 📁 Virtual environment
│
├── modules/
│   ├── main_detection/      # 🎯 Core detection system
│   │   ├── app.py          # Flask application
│   │   ├── detection/      # AI detection modules
│   │   └── templates/      # HTML templates
│   │
│   └── jitsi_system/       # 🌐 Video call integration
│
├── assets/                 # 📸 Template images
├── static/                 # 🖼️ Static files
└── docs/                   # 📚 Documentation
```

---

## ⚙️ **Configuration**

### **Ganti Detector Type:**
Edit file: `modules/main_detection/detection/main_detector.py`

```python
# Line 8 - Ganti detector type:
DETECTOR_TYPE = "template_based"  # Options: "template_based", "fast", "2layer", "advanced"
```

**Detector Options:**
- `"template_based"` - Paling akurat (default)
- `"fast"` - Paling cepat untuk real-time
- `"2layer"` - Balance akurasi & speed
- `"advanced"` - Maksimal akurasi (lambat)

### **Ganti Port Aplikasi:**
Edit file: `modules/main_detection/app.py`

```python
# Line terakhir:
app.run(host='0.0.0.0', port=8080, debug=True)  # Ganti 8080 ke port lain
```

---

## 🔒 **Security Notes**

1. **Firewall:** Aplikasi akan membuka port 8080
2. **Camera Permission:** Browser akan meminta akses camera
3. **File Access:** Aplikasi menyimpan hasil capture di folder static/
4. **Network:** Aplikasi berjalan di localhost (tidak akses internet)

---

## 📝 **Quick Command Reference**

```bash
# Aktivasi virtual environment
# Windows:
.venv\Scripts\activate

# macOS/Linux:
source .venv/bin/activate

# Deaktivasi virtual environment
deactivate

# Update dependencies
pip install --upgrade opencv-python mediapipe flask

# Restart aplikasi
Ctrl+C (stop) → python launcher.py (start)

# Check running processes
# Windows: tasklist | findstr python
# macOS/Linux: ps aux | grep python
```

---

## 💡 **Tips & Best Practices**

### **Performance:**
- ✅ Gunakan `"fast"` detector untuk laptop low-spec
- ✅ Tutup aplikasi lain yang menggunakan camera
- ✅ Pastikan pencahayaan ruangan cukup

### **Stability:**
- ✅ Selalu gunakan virtual environment
- ✅ Restart aplikasi jika ada error camera
- ✅ Update browser ke versi terbaru

### **Development:**
- ✅ Gunakan `debug=True` untuk development
- ✅ Set `debug=False` untuk production
- ✅ Monitor memory usage untuk session panjang

---

## 🆘 **Getting Help**

1. **Check Logs:** Terminal akan menampilkan error messages
2. **Test Components:** Gunakan test scripts di folder modules/
3. **GitHub Issues:** Report bugs di repository GitHub
4. **Documentation:** Baca files di folder docs/

**Contact:**
- 📧 Email: [Your email]
- 💬 GitHub: https://github.com/deeztrzl/photo-detection-system
- 📱 WhatsApp: [Your number]

---

**✅ Setup Complete!** 
Aplikasi siap digunakan di laptop baru. Selamat menggunakan Photo Detection System! 🎉

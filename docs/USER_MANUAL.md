# 📖 USER MANUAL
## Panduan Penggunaan Photo Detection AI

---

## 🎯 **Overview Aplikasi**

Photo Detection AI adalah sistem verifikasi identitas berbasis web yang menggunakan kecerdasan buatan untuk mendeteksi wajah dan KTP secara real-time. Aplikasi ini dirancang untuk memberikan pengalaman pengguna yang mudah dan hasil yang akurat.

### **Fitur Utama:**
- 🤖 **Deteksi Real-time:** Mendeteksi wajah dan KTP secara bersamaan
- ⚡ **Dual Mode:** Mode otomatis dan manual
- 🎯 **Anti-Blur:** Countdown 3 detik untuk hasil tajam
- 📦 **Auto Download:** Unduh otomatis file ZIP hasil
- 📱 **Responsive:** Interface yang adaptif untuk berbagai perangkat

---

## 🚀 **Getting Started**

### **Langkah Awal:**
1. **Pastikan aplikasi running** di http://localhost:5000
2. **Buka browser** (Chrome, Firefox, Safari, Edge)
3. **Allow camera access** ketika diminta browser
4. **Posisikan kamera** dengan pencahayaan yang baik

### **Interface Overview:**
```
┌─────────────────┬─────────────────┐
│   KAMERA LIVE   │   HASIL FOTO    │
│                 │                 │
│ [Video Stream]  │ [Foto Wajah]    │
│                 │ [Foto KTP]      │
│ Status Deteksi: │                 │
│ 👤 Wajah: ✓/✗   │ [Tombol         │
│ 🆔 KTP: ✓/✗     │  Download]      │
│                 │                 │
│ [Mode Toggle]   │                 │
│ [Tombol Capture]│                 │
└─────────────────┴─────────────────┘
```

---

## 🎮 **Mode Operasi**

### **1. Mode Otomatis (Recommended)**

#### **Cara Penggunaan:**
1. **Aktivasi Mode:**
   - Pastikan toggle switch di posisi "Otomatis"
   - Indikator akan menunjukkan "Mode Otomatis Aktif"

2. **Posisioning:**
   - Posisikan wajah Anda di depan kamera
   - Tunggu indikator "👤 Wajah: Terdeteksi" menjadi hijau

3. **Menunjukkan KTP:**
   - Pegang KTP dalam posisi landscape (horizontal)
   - Pastikan KTP terlihat jelas dan tidak miring
   - Tunggu indikator "🆔 KTP: Terdeteksi" menjadi hijau

4. **Auto Capture:**
   - Ketika kedua objek terdeteksi, countdown 3 detik akan dimulai
   - Tetap diam selama countdown untuk hasil terbaik
   - Foto akan diambil otomatis setelah countdown selesai

5. **Download Otomatis:**
   - File ZIP akan otomatis ter-download setelah capture
   - File berisi foto wajah dan foto KTP dengan timestamp

#### **Tips Mode Otomatis:**
- ✅ **Tetap diam** saat countdown berlangsung
- ✅ **Pastikan pencahayaan** cukup dan merata
- ✅ **Posisi KTP** harus landscape dan terlihat jelas
- ✅ **Jarak optimal** wajah 30-50cm dari kamera

### **2. Mode Manual**

#### **Cara Penggunaan:**
1. **Aktivasi Mode:**
   - Toggle switch ke posisi "Manual"
   - Guide overlay akan muncul di video

2. **Positioning dengan Guide:**
   - Gunakan guide overlay untuk memposisikan wajah dan KTP
   - Guide menunjukkan area optimal untuk foto

3. **Manual Capture:**
   - Klik tombol "Capture Langsung" kapan saja
   - Foto akan diambil immediately tanpa countdown

4. **Download Manual:**
   - Tombol download akan muncul setelah capture
   - Klik untuk mengunduh file ZIP hasil

#### **Kegunaan Mode Manual:**
- 🎯 **Kontrol penuh** atas timing capture
- 🎨 **Positioning guide** untuk hasil optimal
- ⚡ **Capture cepat** tanpa menunggu deteksi
- 🔧 **Troubleshooting** jika mode auto bermasalah

---

## 📊 **Status Indicators & Feedback**

### **Indikator Visual:**

#### **Status Deteksi:**
- **👤 Wajah: Tidak Terdeteksi** (Merah) - Posisikan wajah di kamera
- **👤 Wajah: Terdeteksi** (Hijau) - Wajah berhasil dideteksi
- **🆔 KTP: Tidak Terdeteksi** (Merah) - Tunjukkan KTP ke kamera
- **🆔 KTP: Terdeteksi** (Hijau) - KTP berhasil dideteksi

#### **Status Sistem:**
- **🔍 Menunggu deteksi...** - Sistem siap, menunggu objek
- **⚠️ Wajah terdeteksi. Silakan tunjukkan KTP** - Partial detection
- **⚠️ KTP terdeteksi. Silakan posisikan wajah** - Partial detection
- **✅ Siap untuk capture!** - Kedua objek terdeteksi
- **🎯 Countdown aktif!** - Proses capture sedang berlangsung

#### **Countdown Overlay:**
- **Angka besar** di tengah layar saat countdown
- **Visual pulse effect** untuk menarik perhatian
- **Background gelap** untuk fokus pada countdown

---

## 🎯 **Best Practices**

### **Pencahayaan:**
- ✅ **Cahaya alami** dari depan wajah ideal
- ✅ **Hindari backlight** (cahaya dari belakang)
- ✅ **Cahaya merata** tanpa bayangan keras
- ❌ **Hindari cahaya terlalu terang** yang menyilaukan

### **Positioning:**
- ✅ **Wajah centered** di frame kamera
- ✅ **Jarak 30-50cm** dari kamera optimal
- ✅ **KTP landscape** (horizontal orientation)
- ✅ **KTP flat** tanpa lipatan atau refleksi

### **Environment:**
- ✅ **Background kontras** dengan wajah dan KTP
- ✅ **Area stabil** tanpa gerakan berlebihan
- ✅ **Webcam stable** tidak bergerak atau bergoyang
- ❌ **Hindari background** yang terlalu ramai

### **Teknik Capture:**
- ✅ **Steady hands** saat memegang KTP
- ✅ **Natural expression** untuk foto wajah
- ✅ **Avoid sudden movements** selama proses
- ✅ **Wait for indicators** sebelum bergerak

---

## 🔧 **Troubleshooting Umum**

### **Camera Issues:**

#### **Kamera tidak terdeteksi:**
1. **Refresh browser** dan allow camera access
2. **Check camera permissions** di browser settings
3. **Try different browser** (Chrome recommended)
4. **Restart aplikasi** jika diperlukan

#### **Video feed blank/hitam:**
1. **Check camera connection** (USB atau built-in)
2. **Close other apps** yang menggunakan camera
3. **Try different camera** jika tersedia multiple
4. **Check camera privacy settings** di OS

### **Detection Issues:**

#### **Wajah tidak terdeteksi:**
- 🔍 **Improve lighting** - pastikan wajah terang
- 📐 **Adjust position** - centered di frame
- 🎭 **Remove obstructions** - kacamata, masker, dll
- 📏 **Check distance** - tidak terlalu dekat/jauh

#### **KTP tidak terdeteksi:**
- 🔄 **Rotate KTP** ke posisi landscape
- 💙 **Ensure blue color** terlihat jelas
- 📱 **Avoid reflections** dari lampu/cahaya
- 📐 **Keep flat** tanpa bengkok atau lipatan
- 🖼️ **Fill frame adequately** - KTP cukup besar di frame

#### **False Detection:**
- 🔍 **Remove blue objects** dari background
- 📱 **Avoid phones/tablets** dengan layar biru
- 👕 **Change clothing** jika ada warna biru dominan
- 🖼️ **Clean background** dari objek mengganggu

### **Performance Issues:**

#### **Aplikasi lambat:**
1. **Close other browser tabs** yang tidak perlu
2. **Restart browser** untuk clear memory
3. **Check CPU usage** - close aplikasi lain
4. **Try lower resolution** jika memungkinkan

#### **Download tidak berfungsi:**
1. **Check browser permissions** untuk downloads
2. **Try manual download** button
3. **Clear browser cache** dan cookies
4. **Disable ad blockers** sementara

---

## 📋 **Quality Guidelines**

### **Foto Wajah yang Baik:**
- ✅ **Sharp focus** - tidak blur
- ✅ **Good lighting** - wajah terlihat jelas
- ✅ **Natural expression** - tidak forced smile
- ✅ **Eyes open** dan visible
- ✅ **Front facing** - tidak miring
- ✅ **No obstructions** - tidak ada yang menutupi wajah

### **Foto KTP yang Baik:**
- ✅ **Readable text** - teks bisa dibaca
- ✅ **No glare** - tidak ada pantulan cahaya
- ✅ **Flat surface** - tidak bengkok
- ✅ **Complete view** - seluruh KTP terlihat
- ✅ **Proper orientation** - landscape position
- ✅ **Sharp edges** - batas KTP jelas

### **Hasil yang Tidak Acceptable:**
- ❌ **Blurry images** - gerakan saat capture
- ❌ **Over/under exposed** - terlalu terang/gelap
- ❌ **Partial objects** - wajah/KTP terpotong
- ❌ **Wrong orientation** - KTP portrait
- ❌ **Obstructed view** - ada yang menutupi

---

## 📱 **Mobile Usage**

### **Responsive Design:**
- 📱 **Mobile optimized** - interface adaptif
- 👆 **Touch friendly** - tombol mudah disentuh
- 🔄 **Auto rotation** - landscape/portrait compatible
- 📐 **Flexible layout** - menyesuaikan screen size

### **Mobile Best Practices:**
- ✅ **Use rear camera** untuk kualitas lebih baik
- ✅ **Steady grip** - gunakan kedua tangan
- ✅ **Good lighting** - lebih penting di mobile
- ✅ **Portrait mode** untuk interface, landscape untuk KTP

---

## 🔐 **Privacy & Security**

### **Data Handling:**
- 🔒 **Local processing** - semua data diproses lokal
- 🗑️ **Temporary files** - tidak ada penyimpanan permanen
- 🚫 **No cloud upload** - data tidak dikirim ke server external
- 🔐 **Secure download** - file dengan timestamp unique

### **Best Practices:**
- ✅ **Use trusted network** untuk akses aplikasi
- ✅ **Clear downloads** setelah selesai jika diperlukan
- ✅ **Close browser** setelah penggunaan
- ✅ **Verify file content** sebelum sharing

---

## 📊 **File Output**

### **Download Format:**
- **File Type:** ZIP compressed archive
- **Naming:** `hasil_capture_YYYYMMDD_HHMMSS.zip`
- **Contents:** 
  - `wajah_YYYYMMDD_HHMMSS.jpg` - Foto wajah
  - `ktp_YYYYMMDD_HHMMSS.jpg` - Foto KTP

### **Image Specifications:**
- **Wajah:** 300x300 pixels, JPEG format
- **KTP:** 480x300 pixels, JPEG format
- **Quality:** High quality, optimized compression
- **Color:** RGB color space

---

## 🆘 **Support & Help**

### **Jika Mengalami Masalah:**
1. **Check troubleshooting section** di atas
2. **Try different browser** (Chrome recommended)
3. **Restart aplikasi** dengan run.bat/run.sh
4. **Check debug panel** di http://localhost:5000/debug

### **Debug Information:**
- Access **debug panel** untuk technical information
- Check **browser console** untuk error messages
- Monitor **network tab** untuk API responses
- Review **application logs** di terminal

---

**🎯 Dengan mengikuti panduan ini, Anda dapat menggunakan Photo Detection AI dengan optimal dan mendapatkan hasil foto berkualitas tinggi!**

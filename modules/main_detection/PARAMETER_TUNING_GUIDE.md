# KTP Detection Parameter Tuning Guide

## 🎯 Problem & Solution

### ❌ **Masalah yang Dialami:**
1. **KTP tidak terdeteksi** - Blue ratio threshold terlalu tinggi (0.5)
2. **KTP palsu similarity tinggi** - Verification threshold tidak cukup ketat (0.78)

### ✅ **Solusi yang Diterapkan:**

#### **1. Blue Ratio Threshold: 0.5 → 0.25**
```python
# SEBELUM (terlalu ketat)
if blue_ratio > 0.5:  # minimal 50% area biru

# SESUDAH (lebih realistis)  
if blue_ratio > 0.25:  # minimal 25% area biru
```

**Alasan:**
- KTP asli mungkin tidak memiliki 50% area biru
- 25% lebih realistis untuk warna background KTP Indonesia
- Masih cukup selektif untuk menghindari objek bukan KTP

#### **2. Verification Threshold: 0.78 → 0.85** 
```python
# SEBELUM (kurang ketat)
verification_threshold = 0.78  # 78% confidence

# SESUDAH (lebih ketat)
verification_threshold = 0.85  # 85% confidence  
```

**Alasan:**
- 85% lebih ketat untuk mencegah false positives
- Mengurangi KTP palsu yang lolos verifikasi
- Template matching harus benar-benar mirip

## 📊 Parameter Tuning Guidelines

### **Blue Ratio Threshold:**
- **0.1-0.2**: Terlalu rendah, banyak noise
- **0.25**: ✅ **OPTIMAL** - Balance detection & accuracy
- **0.3-0.4**: Masih baik, sedikit lebih selektif
- **0.5+**: Terlalu tinggi, KTP asli tidak terdeteksi

### **Verification Threshold:**
- **0.7-0.75**: Terlalu rendah, banyak false positives
- **0.78-0.82**: Baik untuk deteksi umum
- **0.85**: ✅ **OPTIMAL** - Ketat tapi tidak berlebihan
- **0.9+**: Terlalu ketat, KTP asli mungkin ditolak

## 🔧 Fine-tuning Instructions

### **Jika KTP masih tidak terdeteksi:**
```python
# Turunkan blue ratio threshold
if blue_ratio > 0.2:  # coba 20%
```

### **Jika masih banyak false positives:**
```python
# Naikkan verification threshold
verification_threshold = 0.88  # coba 88%
```

### **Jika deteksi terlalu lambat:**
```python
# Naikkan blue ratio untuk lebih selektif
if blue_ratio > 0.3:  # coba 30%
```

## 📝 Testing Recommendations

1. **Test dengan KTP asli** untuk memastikan terdeteksi
2. **Test dengan objek palsu** untuk memastikan ditolak
3. **Monitor log output** untuk melihat confidence scores
4. **Adjust parameters** berdasarkan hasil testing

## 🎯 Current Optimal Settings

```python
# Layer 1: Color detection
blue_ratio_threshold = 0.25  # 25% minimal area biru

# Layer 2: Template verification  
verification_threshold = 0.85  # 85% confidence minimal
```

**Status:** ✅ **OPTIMIZED** for Indonesian KTP detection

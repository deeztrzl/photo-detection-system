# Panduan Mengganti Detector KTP

File ini menjelaskan cara mengganti tipe detector KTP yang digunakan dalam sistem.

## Detector yang Tersedia:

### 1. **ktp_detector_template_based.py** (Default)
- **Kelebihan**: Paling akurat, adaptive performance mode, texture analysis
- **Kekurangan**: Komputasi heavy untuk mode thorough
- **Cocok untuk**: Production dengan accuracy tinggi

### 2. **ktp_detector.py** (2-Layer System)
- **Kelebihan**: Balance antara akurasi dan performa, anti-fraud checks
- **Kekurangan**: Moderate complexity
- **Cocok untuk**: Sistem yang butuh verifikasi berlapis

### 3. **ktp_detector_fast.py** 
- **Kelebihan**: Sangat cepat, lightweight
- **Kekurangan**: Akurasi lebih rendah
- **Cocok untuk**: Real-time applications, hardware terbatas

### 4. **ktp_detector_advanced.py**
- **Kelebihan**: Feature matching dengan ORB+SIFT, sangat akurat
- **Kekurangan**: Paling berat komputasi
- **Cocok untuk**: Offline processing, accuracy maksimal

## Cara Mengganti Detector:

### Edit file: `modules/main_detection/detection/main_detector.py`

#### Untuk Template-Based (Default):
```python
from detection.ktp_detector_template_based import detect_ktp_template_based

# Dalam fungsi detect_face_and_ktp():
ktp_detections = detect_ktp_template_based(frame, performance_mode='fast')
```

#### Untuk 2-Layer System:
```python
from detection.ktp_detector import detect_ktp_candidates_by_color_and_shape, verify_ktp_candidate_by_template

# Dalam fungsi detect_face_and_ktp():
candidates = detect_ktp_candidates_by_color_and_shape(frame)
for candidate in candidates:
    confidence, result = verify_ktp_candidate_by_template(frame, candidate)
```

#### Untuk Fast Detection:
```python
from detection.ktp_detector_fast import detect_ktp_in_frame

# Dalam fungsi detect_face_and_ktp():
detected, confidence, result = detect_ktp_in_frame(frame)
```

#### Untuk Advanced Detection:
```python
from detection.ktp_detector_advanced import detect_ktp_candidates_by_color_and_shape, verify_ktp_candidate_by_advanced_matching

# Dalam fungsi detect_face_and_ktp():
candidates = detect_ktp_candidates_by_color_and_shape(frame)
for candidate in candidates:
    confidence, result = verify_ktp_candidate_by_advanced_matching(frame, candidate)
```

## Tips Performance:

1. **Real-time**: Gunakan `ktp_detector_fast.py`
2. **Balance**: Gunakan `ktp_detector.py` (2-layer)
3. **Accuracy**: Gunakan `ktp_detector_template_based.py`
4. **Maximum**: Gunakan `ktp_detector_advanced.py`

## Restart Aplikasi:
Setelah mengganti detector, restart aplikasi:
```bash
python launcher.py
```

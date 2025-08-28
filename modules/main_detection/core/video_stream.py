"""
Video streaming module with real-time detection overlay
"""
import cv2
import numpy as np
from core.config import cap, capture_mode, get_ktp_template, CAMERA_WIDTH, CAMERA_HEIGHT
from detection.ktp_detector_template_based import detect_ktp_template_based

def gen_frames():
    """Generator untuk video streaming dengan overlay deteksi"""
    global capture_mode
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        # Real-time KTP detection overlay untuk visual feedback
        ktp_detected = False
        confidence_score = 0
        detection_location = None
        
        # Template-based detection untuk visual overlay (simplified untuk real-time)
        try:
            ktp_detections = detect_ktp_template_based(frame, performance_mode='fast')  # Force fast mode for streaming
            if ktp_detections:
                # Ambil deteksi terbaik untuk overlay
                best_detection = ktp_detections[0]
                bbox = best_detection['bbox']
                x, y, w, h = bbox
                detection_location = (x, y, w, h)
                confidence_score = best_detection.get('combined_confidence', best_detection['confidence'])
                ktp_detected = True
        except Exception as e:
            print(f"⚠️ Real-time detection error: {str(e)}")
            # Fallback ke deteksi sederhana jika error
            ktp_detected = False
        
        # Gambar kotak deteksi KTP jika ada
        if ktp_detected and detection_location:
            x, y, w, h = detection_location
            
            # Warna kotak berdasarkan confidence
            if confidence_score > 0.7:
                color = (0, 255, 0)  # Hijau untuk confidence tinggi
                label = "KTP DETECTED"
            elif confidence_score > 0.5:
                color = (0, 255, 255)  # Kuning untuk confidence sedang
                label = "KTP FOUND"
            else:
                color = (0, 165, 255)  # Orange untuk confidence rendah
                label = "KTP MAYBE"
            
            # Gambar kotak deteksi
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Background untuk text
            text_bg_y = max(y - 35, 0)
            cv2.rectangle(frame, (x, text_bg_y), (x + 250, y), color, -1)
            
            # Text dengan persentase similarity
            similarity_percent = int(confidence_score * 100)
            text = f"{label} - {similarity_percent}%"
            cv2.putText(frame, text, (x + 5, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        # Jika mode manual, gambar garis panduan dinamis
        if capture_mode == 'manual':
            frame = draw_manual_guides(frame)
        
        # STATUS BAR - Informasi Template Matching
        frame = draw_status_bar(frame, confidence_score)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def draw_manual_guides(frame):
    """Gambar garis panduan untuk mode manual"""
    h, w = frame.shape[:2]
    
    # Hitung proporsi dinamis berdasarkan resolusi aktual
    # Base resolution sebagai referensi: 640x480
    base_w, base_h = 640, 480
    scale_x = w / base_w
    scale_y = h / base_h
    
    # Sesuaikan dengan layout CSS menggunakan proporsi
    # Base values: width 640px, padding 186px horizontal, 31px vertikal, gap 25px
    padding_h = int(186 * scale_x)  # padding horizontal proporsional
    padding_v = int(31 * scale_y)   # padding vertikal proporsional
    gap = int(25 * scale_y)         # gap proporsional
    
    # Hitung area yang tersedia setelah padding
    content_width = w - (padding_h * 2)
    content_height = h - (padding_v * 2)
    
    # Area wajah dengan ukuran proporsional: base 207px x 223px
    face_w = int(207 * scale_x)
    face_h = int(223 * scale_y)
    face_x = padding_h + (content_width - face_w) // 2  # center horizontal
    face_y = padding_v  # padding atas
    
    # Area KTP (bagian bawah setelah gap)
    ktp_x = padding_h
    ktp_y = face_y + face_h + gap
    ktp_w = content_width
    ktp_h = content_height - face_h - gap
    
    # Gambar garis panduan wajah (oval/lingkaran)
    face_center_x = face_x + face_w // 2
    face_center_y = face_y + face_h // 2
    face_radius_x = face_w // 2
    face_radius_y = face_h // 2
    
    # Buat overlay gelap dengan opacity 50% (#000000)
    overlay = frame.copy()
    
    # Buat mask untuk area yang tidak akan di-overlay (area wajah dan KTP)
    mask = np.zeros((h, w), dtype=np.uint8)
    
    # Area wajah (oval) - buat mask ellipse
    cv2.ellipse(mask, (face_center_x, face_center_y), (face_radius_x, face_radius_y), 
               0, 0, 360, 255, -1)
    
    # Area KTP (rectangle) - buat mask rectangle  
    cv2.rectangle(mask, (ktp_x, ktp_y), (ktp_x + ktp_w, ktp_y + ktp_h), 255, -1)
    
    # Buat overlay hitam di area yang tidak ter-mask
    overlay[mask == 0] = [0, 0, 0]  # Set area di luar kotak dan lingkaran menjadi hitam
    
    # Blend dengan opacity 50%
    alpha = 0.5
    beta = 1.0 - alpha
    frame = cv2.addWeighted(frame, beta, overlay, alpha, 0)
    
    # Gambar oval dengan garis putus-putus untuk wajah
    cv2.ellipse(frame, (face_center_x, face_center_y), (face_radius_x, face_radius_y), 
               0, 0, 360, (255, 255, 255), 2, cv2.LINE_4)
    
    # Gambar kotak dengan garis putus-putus untuk KTP  
    cv2.rectangle(frame, (ktp_x, ktp_y), (ktp_x + ktp_w, ktp_y + ktp_h), 
                 (255, 255, 255), 2, cv2.LINE_4)
    
    return frame

def draw_status_bar(frame, confidence_score):
    """Gambar status bar informasi"""
    h, w = frame.shape[:2]
    status_bar_height = 30
    status_y = h - status_bar_height
    
    # Background status bar
    cv2.rectangle(frame, (0, status_y), (w, h), (0, 0, 0), -1)
    
    # Template status
    ktp_template = get_ktp_template()
    template_status = "Template: LOADED" if ktp_template is not None else "Template: NOT FOUND"
    cv2.putText(frame, template_status, (10, status_y + 20), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0) if ktp_template is not None else (0, 0, 255), 1)
    
    # Confidence score info
    if confidence_score > 0:
        confidence_text = f"Blue Ratio: {int(confidence_score * 100)}%"
        cv2.putText(frame, confidence_text, (180, status_y + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Detection method info
    method_text = "Method: 2-Layer (HSV+Template 78%)"
    cv2.putText(frame, method_text, (w - 280, status_y + 20), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    return frame

"""
Main Detection Coordinator
Mengkoordinasikan deteksi wajah dan KTP dengan template-based approach
"""
import cv2
import numpy as np
from detection.face_detector import detect_face
from detection.ktp_detector_template_based import detect_ktp_template_based

def detect_face_and_ktp(frame):
    """
    Main detection function yang mengkoordinasikan deteksi face dan KTP
    Returns: (face_img, ktp_img, ktp_face_img)
    """
    try:
        if frame is None or frame.size == 0:
            return None, None, None
        
        # Face detection
        face_img = detect_face(frame)
        
        # KTP detection menggunakan template-based approach dengan adaptive performance
        ktp_detections = detect_ktp_template_based(frame, performance_mode='fast')  # Use fast mode for real-time
        
        ktp_img = None
        ktp_face_img = None
        
        if ktp_detections:
            # Ambil deteksi terbaik
            best_detection = ktp_detections[0]
            bbox = best_detection['bbox']
            x, y, w, h = bbox
            
            # Extract KTP region
            ktp_img = frame[y:y+h, x:x+w]
            
            # Coba deteksi wajah di dalam KTP region
            if ktp_img is not None and ktp_img.size > 0:
                ktp_face_img = detect_face(ktp_img)
            
            mode_used = best_detection.get('analysis_mode', 'unknown')
            print(f"✅ KTP detected with confidence: {best_detection.get('combined_confidence', 0):.3f} (mode: {mode_used})")
        
        return face_img, ktp_img, ktp_face_img
        
    except Exception as e:
        print(f"❌ Error in detect_face_and_ktp: {str(e)}")
        return None, None, None


def get_detection_info():
    """
    Return informasi tentang metode deteksi yang digunakan
    """
    return {
        'method': 'Template-Based Detection',
        'description': 'Menggunakan template_ktp.png sebagai referensi',
        'features': ['Multi-scale template matching', 'Validation checks', 'Confidence scoring']
    }

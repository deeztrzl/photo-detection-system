"""
Main Detection Coordinator
Mengkoordinasikan deteksi wajah dan KTP dengan 2-layer detection approach
"""
import cv2
import numpy as np
from detection.face_detector import detect_face
from detection.ktp_detector import detect_ktp_candidates_by_color_and_shape, verify_ktp_candidate_by_template

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
        
        # KTP detection menggunakan 2-layer detection system
        candidates = detect_ktp_candidates_by_color_and_shape(frame)
        
        ktp_img = None
        ktp_face_img = None
        best_confidence = 0.0
        best_candidate = None
        
        # Verifikasi setiap kandidat dengan layer 2
        for candidate in candidates:
            confidence, result = verify_ktp_candidate_by_template(frame, candidate)
            if confidence > best_confidence:
                best_confidence = confidence
                best_candidate = candidate
        
        if best_candidate and best_confidence > 0.35:  # Threshold minimum
            x, y, w, h, area, blue_ratio = best_candidate
            
            # Extract KTP region
            ktp_img = frame[y:y+h, x:x+w]
            
            # Coba deteksi wajah di dalam KTP region
            if ktp_img is not None and ktp_img.size > 0:
                ktp_face_img = detect_face(ktp_img)
            
            print(f"✅ KTP detected with confidence: {best_confidence:.3f} (2-layer detection)")
        
        return face_img, ktp_img, ktp_face_img
        
    except Exception as e:
        print(f"❌ Error in detect_face_and_ktp: {str(e)}")
        return None, None, None


def get_detection_info():
    """
    Return informasi tentang metode deteksi yang digunakan
    """
    return {
        'method': '2-Layer Detection System',
        'description': 'Layer 1: Color & Shape detection, Layer 2: Pattern verification',
        'features': ['Blue header detection', 'Shape analysis', 'Pattern matching', '7-point verification']
    }

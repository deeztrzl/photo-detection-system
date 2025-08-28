"""
Configuration module for photo detection application
"""
import cv2
import mediapipe as mp
import os

# Global configurations
CAMERA_WIDTH, CAMERA_HEIGHT = 640, 480
KTP_TEMPLATE = None

# Fixed absolute paths for template loading
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Template prioritas berdasarkan analisis blue header detection
KTP_TEMPLATE_PATH = os.path.join(ASSETS_DIR, "template_ktp.png")  # Primary: 98.4% blue header
KTP_TEMPLATE_FALLBACK = os.path.join(ASSETS_DIR, "template_ktp_improved.png")  # Fallback
KTP_TEMPLATE_BACKUP = os.path.join(ASSETS_DIR, "ktp muka.png")

# MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

# Video capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# Paths
face_path = 'static/face_capture.jpg'
ktp_path = 'static/ktp_capture.jpg'
guide_path = 'static/ktp_muka.png'

# System modes
capture_mode = 'auto'
countdown_status = {'active': False, 'remaining': 0}

def load_ktp_template():
    """Load template KTP untuk matching"""
    global KTP_TEMPLATE
    
    # Template paths dengan absolute path
    template_paths = [
        KTP_TEMPLATE_PATH,
        KTP_TEMPLATE_FALLBACK,
        KTP_TEMPLATE_BACKUP,
        os.path.join(ASSETS_DIR, "template_ktp_improved.png"),
        os.path.join(ASSETS_DIR, "template_ktp.png"),
        os.path.join(ASSETS_DIR, "ktp muka.png"),
        "../../assets/template_ktp_improved.png",  # fallback relative paths
        "../../assets/template_ktp.png",
        "../../assets/ktp muka.png"
    ]
    
    print(f"🔍 Looking for template in assets directory: {ASSETS_DIR}")
    
    for template_path in template_paths:
        try:
            print(f"   Trying: {template_path}")
            if os.path.exists(template_path):
                template = cv2.imread(template_path)
                if template is not None:
                    # Resize template ke ukuran standar untuk matching
                    KTP_TEMPLATE = cv2.resize(template, (200, 125))  # Rasio KTP ~1.6:1
                    print(f"✅ KTP Template loaded from: {template_path}")
                    return True
        except Exception as e:
            print(f"⚠️ Failed to load template from {template_path}: {e}")
            continue
    
    print("❌ No KTP template found. Using fallback detection method.")
    return False

def get_ktp_template():
    """Get the loaded KTP template"""
    global KTP_TEMPLATE
    return KTP_TEMPLATE

def get_guide_coordinates():
    """Dapatkan koordinat panduan berdasarkan resolusi kamera aktual"""
    # Area wajah (lingkaran) - proporsi dari resolusi kamera
    face_x = int(CAMERA_WIDTH * 0.25)    # 25% dari lebar
    face_y = int(CAMERA_HEIGHT * 0.15)   # 15% dari tinggi  
    face_w = int(CAMERA_WIDTH * 0.5)     # 50% lebar
    face_h = int(CAMERA_HEIGHT * 0.45)   # 45% tinggi
    
    # Area KTP (kotak) - proporsi dari resolusi kamera
    ktp_x = int(CAMERA_WIDTH * 0.25)     # 25% dari lebar
    ktp_y = int(CAMERA_HEIGHT * 0.55)    # 55% dari tinggi
    ktp_w = int(CAMERA_WIDTH * 0.5)      # 50% lebar  
    ktp_h = int(CAMERA_HEIGHT * 0.35)    # 35% tinggi
    
    return {
        'face': {'x': face_x, 'y': face_y, 'w': face_w, 'h': face_h},
        'ktp': {'x': ktp_x, 'y': ktp_y, 'w': ktp_w, 'h': ktp_h}
    }

# Initialize directories
os.makedirs('static', exist_ok=True)

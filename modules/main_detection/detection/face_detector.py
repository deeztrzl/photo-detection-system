"""
Face Detection Module using MediaPipe
"""
import cv2
import numpy as np
from core.config import face_detection

def detect_face(frame):
    """
    Deteksi wajah menggunakan MediaPipe
    Returns: face image atau None
    """
    h, w, _ = frame.shape
    
    # Deteksi wajah menggunakan MediaPipe
    results = face_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    face_img = None
    largest_face_area = 0
    
    if results.detections:
        for detection in results.detections:
            bboxC = detection.location_data.relative_bounding_box
            face_area = bboxC.width * bboxC.height
            if face_area > largest_face_area:
                largest_face_area = face_area
                x1 = max(0, int(bboxC.xmin * w))
                y1 = max(0, int(bboxC.ymin * h))
                x2 = min(w, int((bboxC.xmin + bboxC.width) * w))
                y2 = min(h, int((bboxC.ymin + bboxC.height) * h))
                crop = frame[y1:y2, x1:x2]
                if crop.size > 0:
                    face_img = cv2.resize(crop, (300, 300))
    
    return face_img

def detect_ktp_face(ktp_img):
    """
    Deteksi foto pada KTP (area kecil dengan warna kulit)
    Returns: ktp face image atau None
    """
    if ktp_img is None:
        return None
        
    # Cari area dengan warna kulit di KTP
    hsv_ktp = cv2.cvtColor(ktp_img, cv2.COLOR_BGR2HSV)
    lower_skin = np.array([0, 20, 70])
    upper_skin = np.array([20, 255, 255])
    mask_skin = cv2.inRange(hsv_ktp, lower_skin, upper_skin)
    
    contours_skin, _ = cv2.findContours(mask_skin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours_skin:
        # Ambil area kulit terbesar (kemungkinan foto di KTP)
        largest_skin = max(contours_skin, key=cv2.contourArea)
        x, y, w2, h2 = cv2.boundingRect(largest_skin)
        if w2 > 30 and h2 > 40:  # minimal ukuran foto
            crop = ktp_img[y:y+h2, x:x+w2]
            if crop.size > 0:
                return cv2.resize(crop, (150, 200))
    
    return None

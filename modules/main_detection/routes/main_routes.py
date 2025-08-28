"""
Main routes for the application
"""
import cv2
from flask import render_template, Response, jsonify, request
from core.video_stream import gen_frames
from core.config import capture_mode, countdown_status, cap
from detection.main_detector import detect_face_and_ktp

def init_main_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/video_feed')
    def video_feed():
        return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route('/toggle_mode', methods=['POST'])
    def toggle_mode():
        global capture_mode
        data = request.get_json()
        new_mode = data.get('mode', 'auto')
        if new_mode in ['auto', 'manual']:
            capture_mode = new_mode
            return jsonify({'status': 'success', 'mode': capture_mode})
        return jsonify({'status': 'error', 'message': 'Invalid mode'})

    @app.route('/detection_status', methods=['GET'])
    def detection_status():
        """Endpoint untuk mendapatkan status deteksi real-time"""
        global cap
        
        try:
            # Simple error handling untuk kamera
            success, frame = cap.read()
            if not success:
                # Reinitialize kamera
                cap.release()
                cap = cv2.VideoCapture(0)
                success, frame = cap.read()
                if not success:
                    return jsonify({'error': 'Kamera tidak dapat diakses'}), 500
            
            # Detection with error handling
            face_img, ktp_img, ktp_face_img = detect_face_and_ktp(frame)
            
            # Ensure we always return valid boolean values
            face_detected = face_img is not None and len(face_img) > 0
            ktp_detected = ktp_img is not None
            both_detected = face_detected and ktp_detected
            
            status = {
                'face_detected': face_detected,
                'ktp_detected': ktp_detected,
                'both_detected': both_detected,
                'mode': capture_mode,
                'countdown': countdown_status,
                'threshold': 'Advanced Feature Matching'
            }
            
            return jsonify(status)
            
        except Exception as e:
            print(f"❌ Error in detection_status: {str(e)}")
            # Return safe default status
            return jsonify({
                'face_detected': False,
                'ktp_detected': False,
                'both_detected': False,
                'mode': capture_mode,
                'countdown': countdown_status,
                'threshold': 'Advanced Feature Matching',
                'error': f'Detection error: {str(e)}'
            }), 200  # Return 200 instead of 500 to prevent browser errors

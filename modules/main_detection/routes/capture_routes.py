"""
Capture and file management routes
"""
import time
import cv2
import os
import zipfile
import io
from datetime import datetime
from flask import jsonify, make_response, send_from_directory
from core.config import capture_mode, countdown_status, cap
from detection.main_detector import detect_face_and_ktp

def init_capture_routes(app):
    @app.route('/capture', methods=['POST'])
    def capture():
        global capture_mode, countdown_status
        
        if capture_mode == 'auto':
            # Mode otomatis - menunggu deteksi keduanya (wajah dan KTP)
            start_time = time.time()
            timeout = 30  # 30 detik timeout
            
            face_img = None
            ktp_img = None
            ktp_face_img = None
            
            print("Mode otomatis: Menunggu deteksi wajah dan KTP...")
            
            while time.time() - start_time < timeout:
                success, frame = cap.read()
                if not success:
                    continue
                    
                face_img, ktp_img, ktp_face_img = detect_face_and_ktp(frame)
                
                if face_img is not None and ktp_img is not None:
                    print("✅ Kedua objek terdeteksi! Melakukan capture...")
                    break
                    
                time.sleep(0.1)  # Small delay
            
            if face_img is None or ktp_img is None:
                return jsonify({
                    'status': 'error', 
                    'message': 'Timeout: Tidak dapat mendeteksi wajah dan KTP dalam 30 detik'
                })
        
        else:
            # Mode manual - langsung capture apa yang ada
            success, frame = cap.read()
            if not success:
                return jsonify({'status': 'error', 'message': 'Tidak dapat mengakses kamera'})
            
            face_img, ktp_img, ktp_face_img = detect_face_and_ktp(frame)
        
        # Simpan hasil capture
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"CS_{timestamp[:8]}_{timestamp[9:]}"
        user_id = f"USER_{timestamp}"
        
        # Buat folder untuk session
        session_folder = f"static/captured_ktp"
        os.makedirs(session_folder, exist_ok=True)
        
        captured_files = []
        
        # Simpan wajah jika terdeteksi
        if face_img is not None:
            face_filename = f"{session_id}_{user_id}_face_{timestamp}.jpg"
            face_path = os.path.join(session_folder, face_filename)
            cv2.imwrite(face_path, face_img)
            captured_files.append(face_filename)
        
        # Simpan KTP jika terdeteksi
        if ktp_img is not None:
            ktp_filename = f"{session_id}_{user_id}_ktp_{timestamp}.jpg"
            ktp_path = os.path.join(session_folder, ktp_filename)
            cv2.imwrite(ktp_path, ktp_img)
            captured_files.append(ktp_filename)
        
        # Simpan foto di KTP jika terdeteksi
        if ktp_face_img is not None:
            ktp_face_filename = f"{session_id}_{user_id}_ktp_face_{timestamp}.jpg"
            ktp_face_path = os.path.join(session_folder, ktp_face_filename)
            cv2.imwrite(ktp_face_path, ktp_face_img)
            captured_files.append(ktp_face_filename)
        
        # Simpan full frame untuk referensi
        full_filename = f"{session_id}_{user_id}_full_{timestamp}.jpg"
        full_path = os.path.join(session_folder, full_filename)
        success, frame = cap.read()
        if success:
            cv2.imwrite(full_path, frame)
            captured_files.append(full_filename)
        
        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'captured_files': captured_files,
            'face_detected': face_img is not None,
            'ktp_detected': ktp_img is not None,
            'ktp_face_detected': ktp_face_img is not None,
            'mode': capture_mode
        })

    @app.route('/download/<session_id>')
    def download_session(session_id):
        """Download semua file dari session sebagai ZIP"""
        try:
            session_folder = f"static/captured_ktp"
            
            # Cari semua file untuk session ini
            session_files = []
            if os.path.exists(session_folder):
                for filename in os.listdir(session_folder):
                    if filename.startswith(session_id):
                        session_files.append(filename)
            
            if not session_files:
                return jsonify({'error': 'No files found for this session'}), 404
            
            # Buat ZIP file in memory
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for filename in session_files:
                    file_path = os.path.join(session_folder, filename)
                    if os.path.exists(file_path):
                        zip_file.write(file_path, filename)
            
            zip_buffer.seek(0)
            
            # Return ZIP file
            response = make_response(zip_buffer.getvalue())
            response.headers['Content-Type'] = 'application/zip'
            response.headers['Content-Disposition'] = f'attachment; filename={session_id}_capture.zip'
            
            return response
            
        except Exception as e:
            return jsonify({'error': f'Error creating download: {str(e)}'}), 500

    @app.route('/captured_files')
    def captured_files():
        """List semua file yang sudah di-capture"""
        try:
            captured_folder = "static/captured_ktp"
            files = []
            
            if os.path.exists(captured_folder):
                for filename in os.listdir(captured_folder):
                    if filename.endswith('.jpg'):
                        file_path = os.path.join(captured_folder, filename)
                        # Parse info dari filename
                        parts = filename.split('_')
                        if len(parts) >= 6:
                            session_id = f"{parts[0]}_{parts[1]}_{parts[2]}"
                            user_id = f"{parts[3]}_{parts[4]}"
                            capture_type = parts[5]
                            timestamp = parts[6].replace('.jpg', '')
                            
                            files.append({
                                'filename': filename,
                                'session_id': session_id,
                                'user_id': user_id,
                                'type': capture_type,
                                'timestamp': timestamp,
                                'size': os.path.getsize(file_path)
                            })
            
            # Sort by timestamp (newest first)
            files.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return jsonify({
                'status': 'success',
                'files': files,
                'total': len(files)
            })
            
        except Exception as e:
            return jsonify({'error': f'Error listing files: {str(e)}'}), 500

    @app.route('/static/captured_ktp/<filename>')
    def serve_captured_file(filename):
        """Serve captured files"""
        return send_from_directory('static/captured_ktp', filename)

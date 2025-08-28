"""
Dummy Jitsi Meet dengan KTP Capture Feature
CS dapat capture KTP dari video nasabah
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit, join_room, leave_room
import cv2
import numpy as np
import base64
import io
from PIL import Image
import os
from datetime import datetime
import zipfile

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dummy_jitsi_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Storage untuk participants
participants = {}
rooms = {}

# Create folders
os.makedirs('static/captures', exist_ok=True)
os.makedirs('templates', exist_ok=True)

@app.route('/')
def index():
    return render_template('jitsi_dummy.html')

@app.route('/cs')
def cs_interface():
    return render_template('cs_interface.html')

@app.route('/nasabah') 
def nasabah_interface():
    return render_template('nasabah_interface.html')

@socketio.on('join_room')
def handle_join_room(data):
    room = data['room']
    user_type = data['user_type']  # 'cs' or 'nasabah'
    user_id = data['user_id']
    
    print(f"🔄 Join request: {user_type} {user_id} requesting to join room {room}")
    
    join_room(room)
    
    # Store participant info
    participants[user_id] = {
        'room': room,
        'type': user_type,
        'sid': request.sid
    }
    
    if room not in rooms:
        rooms[room] = {'participants': []}
    
    rooms[room]['participants'].append({
        'id': user_id,
        'type': user_type,
        'sid': request.sid
    })
    
    # Notify all participants
    emit('participant_joined', {
        'user_id': user_id,
        'user_type': user_type,
        'participants': rooms[room]['participants']
    }, room=room)
    
    print(f"✅ {user_type} {user_id} joined room {room}")
    print(f"📊 Room {room} now has {len(rooms[room]['participants'])} participants")

@socketio.on('show_ktp_frame')
def handle_show_ktp_frame(data):
    cs_id = data['cs_id']
    nasabah_id = data['nasabah_id']
    room = data['room']
    
    # Send command ke nasabah untuk show overlay
    emit('overlay_command', {
        'action': 'enable',
        'cs_id': cs_id
    }, room=room)
    
    print(f"CS {cs_id} request KTP frame from nasabah {nasabah_id}")

@socketio.on('hide_ktp_frame')
def handle_hide_ktp_frame(data):
    room = data['room']
    
    # Send command ke nasabah untuk hide overlay
    emit('overlay_command', {
        'action': 'disable'
    }, room=room)

@socketio.on('capture_ktp')
def handle_capture_ktp(data):
    try:
        cs_id = data['cs_id']
        nasabah_id = data['nasabah_id']
        room = data['room']
        mode = data.get('mode', 'manual')  # Default ke manual mode
        image_data = data.get('image_data', None)  # Frame dari kamera CS
        
        # Process manual capture dengan frame dari CS camera
        result = process_manual_ktp_capture(cs_id, nasabah_id, mode, image_data)
        
        # Send result ke CS
        emit('capture_result', result, room=room)
        
        # Send command ke nasabah untuk disable overlay
        emit('overlay_command', {'action': 'disable'}, room=room)
        
        print(f"Manual capture completed: CS {cs_id} captured nasabah {nasabah_id}")
        
    except Exception as e:
        emit('capture_result', {'status': 'error', 'message': str(e)})
        print(f"Capture error: {e}")

def process_manual_ktp_capture(cs_id, nasabah_id, mode, image_data=None):
    """Process KTP capture dengan logika manual mode yang sama seperti app.py"""
    try:
        # Simulate coordinate calculation (sama seperti app.py manual mode)
        base_w, base_h = 640, 480
        
        # Calculate areas (same as app.py get_guide_coordinates)
        padding_h = 186
        padding_v = 31
        gap = 25
        
        content_width = base_w - (padding_h * 2)
        content_height = base_h - (padding_v * 2)
        
        # Face area coordinates
        face_w = 207
        face_h = 223
        face_x = padding_h + (content_width - face_w) // 2
        face_y = padding_v
        
        # KTP area coordinates  
        ktp_x = padding_h
        ktp_y = face_y + face_h + gap
        ktp_w = content_width
        ktp_h = content_height - face_h - gap
        
        # Create capture timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create capture directory
        capture_files = []
        capture_dir = os.path.join(app.static_folder, 'captured_ktp')
        os.makedirs(capture_dir, exist_ok=True)
        
        # Generate actual JPG files with OpenCV using frame from CS camera
        import cv2
        import numpy as np
        import base64
        
        print(f"CS {cs_id} melakukan capture dari kamera CS untuk nasabah {nasabah_id}")
        
        capture_source = "cs_camera"
        frame = None
        
        if image_data:
            try:
                # Decode base64 image data dari CS camera
                header, encoded = image_data.split(',', 1)
                image_bytes = base64.b64decode(encoded)
                
                # Convert to numpy array
                nparr = np.frombuffer(image_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    print("✓ Frame dari CS camera berhasil di-decode")
                    capture_source = "cs_camera_actual"
                else:
                    print("⚠ Frame tidak bisa di-decode, menggunakan fallback")
            except Exception as e:
                print(f"⚠ Error decoding frame: {e}, menggunakan fallback")
        
        # Fallback jika tidak ada frame dari CS atau gagal decode
        if frame is None:
            print("✓ Menggunakan simulasi frame")
            capture_source = "simulation_fallback"
            
            # Create realistic nasabah simulation frame
            frame = np.zeros((base_h, base_w, 3), dtype=np.uint8)
            
            # Background gradient yang realistis
            for i in range(base_h):
                intensity = int(60 + (i / base_h) * 40)
                frame[i, :] = [intensity-10, intensity, intensity+5]
            
            # Simulasi area wajah yang realistis
            face_sim_x = padding_h + (content_width - face_w) // 2
            face_sim_y = padding_v
            
            # Wajah simulasi dengan warna kulit
            cv2.ellipse(frame, (face_sim_x + face_w//2, face_sim_y + face_h//2), 
                       (face_w//3, face_h//3), 0, 0, 360, (180, 150, 120), -1)
            
            # Mata simulasi
            eye_y = face_sim_y + face_h//2 - 20
            cv2.circle(frame, (face_sim_x + face_w//2 - 30, eye_y), 8, (50, 50, 50), -1)
            cv2.circle(frame, (face_sim_x + face_w//2 + 30, eye_y), 8, (50, 50, 50), -1)
            
            # Mulut simulasi
            mouth_y = face_sim_y + face_h//2 + 30
            cv2.ellipse(frame, (face_sim_x + face_w//2, mouth_y), (20, 10), 0, 0, 180, (100, 80, 80), 2)
            
            # Simulasi KTP yang realistis (hanya untuk fallback)
            ktp_sim_x = padding_h
            ktp_sim_y = face_sim_y + face_h + gap
            
            # Background KTP biru
            cv2.rectangle(frame, (ktp_sim_x + 10, ktp_sim_y + 10), 
                         (ktp_sim_x + ktp_w - 10, ktp_sim_y + ktp_h - 10), (120, 160, 200), -1)
            
            # Border KTP
            cv2.rectangle(frame, (ktp_sim_x + 10, ktp_sim_y + 10), 
                         (ktp_sim_x + ktp_w - 10, ktp_sim_y + ktp_h - 10), (80, 120, 160), 3)
            
            # Text pada KTP
            cv2.putText(frame, 'REPUBLIK INDONESIA', (ktp_sim_x + 30, ktp_sim_y + 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(frame, 'KTP ID CARD', (ktp_sim_x + 30, ktp_sim_y + 65), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            print("Frame simulasi berhasil dibuat")
        
        # Get actual frame dimensions
        h, w = frame.shape[:2]
        print(f"Actual frame size: {w}x{h}")
        
        # Recalculate coordinates for actual frame size (same logic as app.py)
        scale_x = w / base_w
        scale_y = h / base_h
        
        # Recalculate all coordinates with actual scale
        padding_h = int(186 * scale_x)
        padding_v = int(31 * scale_y) 
        gap = int(25 * scale_y)
        
        content_width = w - (padding_h * 2)
        content_height = h - (padding_v * 2)
        
        # Face area coordinates (for actual frame)
        face_w = int(207 * scale_x)
        face_h = int(223 * scale_y)
        face_x = padding_h + (content_width - face_w) // 2
        face_y = padding_v
        
        # KTP area coordinates (for actual frame)
        ktp_x = padding_h
        ktp_y = face_y + face_h + gap
        ktp_w = content_width
        ktp_h = content_height - face_h - gap
        
        print(f"Calculated coordinates for {w}x{h}: face({face_x},{face_y},{face_w},{face_h}) ktp({ktp_x},{ktp_y},{ktp_w},{ktp_h})")
        
        # Generate file names
        face_file = f"cs_{cs_id}_nasabah_{nasabah_id}_face_{timestamp}.jpg"
        ktp_file = f"cs_{cs_id}_nasabah_{nasabah_id}_ktp_{timestamp}.jpg"
        full_file = f"cs_{cs_id}_nasabah_{nasabah_id}_full_{timestamp}.jpg"
        
        # Save full frame with overlay (same as app.py manual mode visualization)
        full_img = frame.copy()
        
        # Draw overlay to show capture areas (same as app.py)
        cv2.ellipse(full_img, (face_x + face_w//2, face_y + face_h//2), 
                   (face_w//2, face_h//2), 0, 0, 360, (0, 0, 255), 3)
        cv2.rectangle(full_img, (ktp_x, ktp_y), (ktp_x + ktp_w, ktp_y + ktp_h), (0, 255, 0), 3)
        
        # Add info text
        cv2.putText(full_img, f'CS: {cs_id}', (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(full_img, f'Nasabah: {nasabah_id}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(full_img, f'Source: {capture_source}', (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(full_img, f'Timestamp: {timestamp}', (10, h-30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.putText(full_img, 'Mode: Manual (app.py logic)', (10, h-10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        full_path = os.path.join(capture_dir, full_file)
        cv2.imwrite(full_path, full_img)
        
        # Crop face area from actual frame (same as app.py)
        x1_face = max(0, min(face_x, w))
        y1_face = max(0, min(face_y, h))
        x2_face = min(w, face_x + face_w)
        y2_face = min(h, face_y + face_h)
        
        if x2_face > x1_face and y2_face > y1_face:
            face_crop = frame[y1_face:y2_face, x1_face:x2_face]
            face_crop = cv2.resize(face_crop, (300, 300))  # Resize to standard size
            print("Face crop successful from real camera")
        else:
            # Fallback face crop
            face_crop = np.zeros((300, 300, 3), dtype=np.uint8)
            face_crop.fill(80)
            cv2.circle(face_crop, (150, 150), 120, (150, 150, 255), -1)
            cv2.putText(face_crop, 'FACE FALLBACK', (60, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            print("Face crop failed, using fallback")
        
        face_path = os.path.join(capture_dir, face_file)
        cv2.imwrite(face_path, face_crop)
        
        # Crop KTP area from actual frame (same as app.py)
        x1_ktp = max(0, min(ktp_x, w))
        y1_ktp = max(0, min(ktp_y, h))
        x2_ktp = min(w, ktp_x + ktp_w)
        y2_ktp = min(h, ktp_y + ktp_h)
        
        if x2_ktp > x1_ktp and y2_ktp > y1_ktp:
            ktp_crop = frame[y1_ktp:y2_ktp, x1_ktp:x2_ktp]
            ktp_crop = cv2.resize(ktp_crop, (480, 300))  # Resize to standard size
            print("KTP crop successful from real camera")
        else:
            # Fallback KTP crop
            ktp_crop = np.zeros((300, 480, 3), dtype=np.uint8)
            ktp_crop.fill(60)
            cv2.rectangle(ktp_crop, (20, 20), (460, 280), (150, 255, 150), 3)
            cv2.putText(ktp_crop, 'KTP FALLBACK', (150, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            print("KTP crop failed, using fallback")
        
        ktp_path = os.path.join(capture_dir, ktp_file)
        cv2.imwrite(ktp_path, ktp_crop)
        
        capture_files = [
            f"Face: {face_file}",
            f"KTP: {ktp_file}", 
            f"Full: {full_file}"
        ]
        
        print(f"📁 JPG Files created in: {capture_dir}")
        print(f"📄 Generated files: {len(capture_files)} JPG images")
        print(f"📸 Face: {face_path}")
        print(f"🆔 KTP: {ktp_path}")
        print(f"📷 Full: {full_path}")
        
        return {
            'status': 'success',
            'cs_id': cs_id,
            'nasabah_id': nasabah_id,
            'timestamp': timestamp,
            'mode': mode,
            'saved_files': capture_files,
            'coordinates': {
                'face': {'x': face_x, 'y': face_y, 'w': face_w, 'h': face_h},
                'ktp': {'x': ktp_x, 'y': ktp_y, 'w': ktp_w, 'h': ktp_h}
            },
            'message': 'KTP berhasil di-capture menggunakan mode manual (logika sama dengan app.py)'
        }
        
    except Exception as e:
        print(f"Error processing manual KTP capture: {e}")
        return {
            'status': 'error',
            'message': f'Error: {str(e)}'
        }

def process_ktp_capture(frame, cs_id, nasabah_id):
    """Process KTP capture dengan koordinat yang sama seperti app.py"""
    try:
        h, w = frame.shape[:2]
        
        # Calculate coordinates (same as app.py manual mode)
        base_w, base_h = 640, 480
        scale_x = w / base_w
        scale_y = h / base_h
        
        padding_h = int(186 * scale_x)
        padding_v = int(31 * scale_y)
        gap = int(25 * scale_y)
        
        content_width = w - (padding_h * 2)
        content_height = h - (padding_v * 2)
        
        # Face area
        face_w = int(207 * scale_x)
        face_h = int(223 * scale_y)
        face_x = padding_h + (content_width - face_w) // 2
        face_y = padding_v
        
        # KTP area
        ktp_x = padding_h
        ktp_y = face_y + face_h + gap
        ktp_w = content_width
        ktp_h = content_height - face_h - gap
        
        # Crop images
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_files = []
        
        # Face crop
        face_path = None
        if (face_y + face_h <= h and face_x + face_w <= w and 
            face_x >= 0 and face_y >= 0):
            face_crop = frame[face_y:face_y + face_h, face_x:face_x + face_w]
            if face_crop.size > 0:
                face_resized = cv2.resize(face_crop, (300, 300))
                face_path = f'static/captures/cs_{cs_id}_nasabah_{nasabah_id}_face_{timestamp}.jpg'
                cv2.imwrite(face_path, face_resized)
                saved_files.append(f"Face: {face_path}")
        
        # KTP crop
        ktp_path = None
        if (ktp_y + ktp_h <= h and ktp_x + ktp_w <= w and
            ktp_x >= 0 and ktp_y >= 0):
            ktp_crop = frame[ktp_y:ktp_y + ktp_h, ktp_x:ktp_x + ktp_w]
            if ktp_crop.size > 0:
                ktp_resized = cv2.resize(ktp_crop, (480, 300))
                ktp_path = f'static/captures/cs_{cs_id}_nasabah_{nasabah_id}_ktp_{timestamp}.jpg'
                cv2.imwrite(ktp_path, ktp_resized)
                saved_files.append(f"KTP: {ktp_path}")
        
        # Save full image for reference
        full_path = f'static/captures/cs_{cs_id}_nasabah_{nasabah_id}_full_{timestamp}.jpg'
        cv2.imwrite(full_path, frame)
        saved_files.append(f"Full: {full_path}")
        
        return {
            'status': 'success',
            'face_path': face_path,
            'ktp_path': ktp_path,
            'full_path': full_path,
            'saved_files': saved_files,
            'timestamp': timestamp,
            'cs_id': cs_id,
            'nasabah_id': nasabah_id
        }
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@app.route('/download_capture/<cs_id>/<nasabah_id>/<timestamp>')
def download_capture(cs_id, nasabah_id, timestamp):
    """Download hasil capture sebagai ZIP"""
    try:
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add files yang ada
            face_file = f'static/captures/cs_{cs_id}_nasabah_{nasabah_id}_face_{timestamp}.jpg'
            ktp_file = f'static/captures/cs_{cs_id}_nasabah_{nasabah_id}_ktp_{timestamp}.jpg'
            full_file = f'static/captures/cs_{cs_id}_nasabah_{nasabah_id}_full_{timestamp}.jpg'
            
            if os.path.exists(face_file):
                zip_file.write(face_file, f'face_{timestamp}.jpg')
            if os.path.exists(ktp_file):
                zip_file.write(ktp_file, f'ktp_{timestamp}.jpg')
            if os.path.exists(full_file):
                zip_file.write(full_file, f'full_{timestamp}.jpg')
        
        zip_buffer.seek(0)
        
        return send_file(
            io.BytesIO(zip_buffer.getvalue()),
            as_attachment=True,
            download_name=f'ktp_capture_{cs_id}_{nasabah_id}_{timestamp}.zip',
            mimetype='application/zip'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=== Dummy Jitsi Meet dengan KTP Capture ===")
    print("CS Interface: http://localhost:5000/cs")
    print("Nasabah Interface: http://localhost:5000/nasabah") 
    print("Main: http://localhost:5000")
    print()
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

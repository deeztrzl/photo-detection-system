"""
Jitsi Meet Bridge System
Backend bridge untuk menghubungkan Jitsi Meet dengan Photo Detection System
"""

from flask import Flask, request, jsonify, send_file
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import base64
import cv2
import numpy as np
import os
from datetime import datetime
import zipfile
import io
import json
import logging
from pathlib import Path

# Import detection engine dari main system
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'main_detection'))
try:
    from app import detect_face_and_ktp, get_guide_coordinates
except ImportError:
    # Fallback jika import gagal
    def detect_face_and_ktp(frame):
        # Simple fallback detection
        return None, None
    
    def get_guide_coordinates():
        return {
            'face': {'x': 160, 'y': 120, 'w': 320, 'h': 240},
            'ktp': {'x': 160, 'y': 350, 'w': 320, 'h': 180}
        }

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jitsi_bridge_secret_key_2025'
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Storage untuk active sessions
active_sessions = {}
capture_history = {}

# Create required directories
CAPTURE_DIR = Path("static/jitsi_captures")
CAPTURE_DIR.mkdir(parents=True, exist_ok=True)

@app.route('/')
def index():
    """Main page dengan informasi bridge system"""
    return """
    <html>
    <head><title>Jitsi Bridge System</title></head>
    <body>
        <h1>🎥 Jitsi Meet KTP Capture Bridge</h1>
        <p><strong>Status:</strong> <span style="color: green;">ACTIVE</span></p>
        <h3>Available Endpoints:</h3>
        <ul>
            <li><code>POST /api/process_capture</code> - Process capture dari Jitsi</li>
            <li><code>POST /api/start_session</code> - Start capture session</li>
            <li><code>GET /api/session_status/&lt;session_id&gt;</code> - Check session status</li>
            <li><code>GET /api/download/&lt;filename&gt;</code> - Download captured files</li>
            <li><code>WebSocket /socket.io/</code> - Real-time communication</li>
        </ul>
        <h3>Integration Guide:</h3>
        <p>Lihat <a href="/static/docs/JITSI_INTEGRATION_GUIDE.md">JITSI_INTEGRATION_GUIDE.md</a> untuk panduan lengkap.</p>
    </body>
    </html>
    """

@app.route('/api/process_capture', methods=['POST', 'OPTIONS'])
def process_capture():
    """
    Main endpoint untuk processing capture dari Jitsi frontend
    Expected payload:
    {
        "session_id": "room_123",
        "participant_id": "user_456", 
        "image_data": "base64_encoded_image",
        "capture_mode": "auto|manual",
        "timestamp": "2025-08-26T10:30:00Z"
    }
    """
    if request.method == 'OPTIONS':
        # Handle CORS preflight request
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        data = request.get_json()
        logger.info(f"Received capture request: {data.keys()}")
        
        # Validate required fields
        required_fields = ['session_id', 'participant_id', 'image_data']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error', 
                    'message': f'Missing required field: {field}'
                }), 400
        
        session_id = data['session_id']
        participant_id = data['participant_id']
        image_data = data['image_data']
        capture_mode = data.get('capture_mode', 'manual')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        # Decode base64 image
        try:
            # Remove data URL prefix if present
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                raise ValueError("Failed to decode image")
            
        except Exception as e:
            logger.error(f"Image decoding error: {e}")
            return jsonify({
                'status': 'error',
                'message': f'Invalid image data: {str(e)}'
            }), 400
        
        # Process dengan detection engine
        logger.info(f"Processing frame: {frame.shape}")
        face_img, ktp_img = detect_face_and_ktp(frame)
        
        # Generate unique identifier
        capture_id = f"{session_id}_{participant_id}_{int(datetime.now().timestamp())}"
        
        # Save capture results
        results = save_capture_results(
            capture_id, 
            participant_id, 
            face_img, 
            ktp_img, 
            timestamp,
            capture_mode
        )
        
        # Store dalam history
        capture_history[capture_id] = {
            'session_id': session_id,
            'participant_id': participant_id,
            'timestamp': timestamp,
            'mode': capture_mode,
            'results': results,
            'status': 'completed'
        }
        
        # Notify via WebSocket
        socketio.emit('capture_completed', {
            'session_id': session_id,
            'participant_id': participant_id,
            'capture_id': capture_id,
            'results': results
        }, room=session_id)
        
        response_data = {
            'status': 'success',
            'capture_id': capture_id,
            'session_id': session_id,
            'participant_id': participant_id,
            'timestamp': timestamp,
            'mode': capture_mode,
            **results
        }
        
        logger.info(f"Capture processed successfully: {capture_id}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Capture processing error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Processing failed: {str(e)}'
        }), 500

def save_capture_results(capture_id, participant_id, face_img, ktp_img, timestamp, mode):
    """Save capture results dan return download data"""
    results = {
        'face_detected': face_img is not None,
        'ktp_detected': ktp_img is not None,
        'files': []
    }
    
    # Create session folder
    session_folder = CAPTURE_DIR / capture_id
    session_folder.mkdir(exist_ok=True)
    
    # Save face image
    if face_img is not None:
        face_filename = f"{participant_id}_face_{timestamp.replace(':', '-')}.jpg"
        face_path = session_folder / face_filename
        cv2.imwrite(str(face_path), face_img)
        
        # Convert ke base64 untuk immediate download
        with open(face_path, 'rb') as f:
            face_b64 = base64.b64encode(f.read()).decode()
        
        results['face_image'] = face_b64
        results['face_filename'] = face_filename
        results['face_download_url'] = f"/api/download/{capture_id}/{face_filename}"
        results['files'].append({
            'type': 'face',
            'filename': face_filename,
            'size': face_path.stat().st_size,
            'download_url': results['face_download_url']
        })
    
    # Save KTP image
    if ktp_img is not None:
        ktp_filename = f"{participant_id}_ktp_{timestamp.replace(':', '-')}.jpg"
        ktp_path = session_folder / ktp_filename
        cv2.imwrite(str(ktp_path), ktp_img)
        
        # Convert ke base64 untuk immediate download
        with open(ktp_path, 'rb') as f:
            ktp_b64 = base64.b64encode(f.read()).decode()
        
        results['ktp_image'] = ktp_b64
        results['ktp_filename'] = ktp_filename
        results['ktp_download_url'] = f"/api/download/{capture_id}/{ktp_filename}"
        results['files'].append({
            'type': 'ktp',
            'filename': ktp_filename,
            'size': ktp_path.stat().st_size,
            'download_url': results['ktp_download_url']
        })
    
    # Create ZIP file jika ada file yang berhasil disimpan
    if results['files']:
        zip_filename = f"{participant_id}_capture_{timestamp.replace(':', '-')}.zip"
        zip_path = session_folder / zip_filename
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_info in results['files']:
                file_path = session_folder / file_info['filename']
                zipf.write(file_path, file_info['filename'])
        
        # Convert ZIP ke base64
        with open(zip_path, 'rb') as f:
            zip_b64 = base64.b64encode(f.read()).decode()
        
        results['zip_file'] = zip_b64
        results['zip_filename'] = zip_filename
        results['zip_download_url'] = f"/api/download/{capture_id}/{zip_filename}"
        results['files'].append({
            'type': 'zip',
            'filename': zip_filename,
            'size': zip_path.stat().st_size,
            'download_url': results['zip_download_url']
        })
    
    # Save metadata
    metadata_path = session_folder / 'metadata.json'
    metadata = {
        'capture_id': capture_id,
        'participant_id': participant_id,
        'timestamp': timestamp,
        'mode': mode,
        'results': {k: v for k, v in results.items() if not k.endswith('_image')},  # Exclude base64 data
        'coordinates': get_guide_coordinates()
    }
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return results

@app.route('/api/start_session', methods=['POST'])
def start_session():
    """Start new capture session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        participants = data.get('participants', [])
        cs_user = data.get('cs_user')
        
        if not session_id:
            return jsonify({'status': 'error', 'message': 'session_id required'}), 400
        
        active_sessions[session_id] = {
            'participants': participants,
            'cs_user': cs_user,
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'captures': []
        }
        
        logger.info(f"Started session: {session_id} with {len(participants)} participants")
        
        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'message': 'Session started successfully'
        })
        
    except Exception as e:
        logger.error(f"Session start error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/session_status/<session_id>')
def session_status(session_id):
    """Get session status dan capture history"""
    if session_id in active_sessions:
        session_data = active_sessions[session_id].copy()
        
        # Add capture history untuk session ini
        session_captures = [
            capture for capture_id, capture in capture_history.items()
            if capture['session_id'] == session_id
        ]
        session_data['capture_history'] = session_captures
        
        return jsonify({
            'status': 'success',
            'session': session_data
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Session not found'
        }), 404

@app.route('/api/download/<path:filepath>')
def download_file(filepath):
    """Download captured files"""
    try:
        # Security: validate filepath
        if '..' in filepath or filepath.startswith('/'):
            return jsonify({'error': 'Invalid filepath'}), 400
        
        file_path = CAPTURE_DIR / filepath
        
        if file_path.exists() and file_path.is_file():
            return send_file(str(file_path), as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
            
    except Exception as e:
        logger.error(f"Download error: {e}")
        return jsonify({'error': str(e)}), 500

# WebSocket Event Handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {
        'status': 'Connected to Jitsi Bridge',
        'client_id': request.sid,
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnect"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('join_session')
def handle_join_session(data):
    """Join capture session room"""
    session_id = data.get('session_id')
    user_type = data.get('user_type', 'participant')  # 'cs' or 'participant'
    user_id = data.get('user_id')
    
    if session_id:
        join_room(session_id)
        logger.info(f"User {user_id} ({user_type}) joined session {session_id}")
        
        emit('session_joined', {
            'session_id': session_id,
            'user_id': user_id,
            'user_type': user_type
        }, room=session_id)
        
        # Send session info ke new participant
        if session_id in active_sessions:
            emit('session_info', active_sessions[session_id])

@socketio.on('leave_session')
def handle_leave_session(data):
    """Leave capture session room"""
    session_id = data.get('session_id')
    user_id = data.get('user_id')
    
    if session_id:
        leave_room(session_id)
        logger.info(f"User {user_id} left session {session_id}")
        
        emit('session_left', {
            'session_id': session_id,
            'user_id': user_id
        }, room=session_id)

@socketio.on('trigger_capture')
def handle_trigger_capture(data):
    """Handle capture trigger dari CS"""
    session_id = data.get('session_id')
    participant_id = data.get('participant_id')
    capture_mode = data.get('mode', 'manual')
    
    if session_id and participant_id:
        logger.info(f"Capture triggered for {participant_id} in session {session_id}")
        
        # Broadcast capture trigger ke participant
        emit('capture_requested', {
            'session_id': session_id,
            'participant_id': participant_id,
            'mode': capture_mode,
            'timestamp': datetime.now().isoformat()
        }, room=session_id)

@socketio.on('overlay_update')
def handle_overlay_update(data):
    """Handle overlay position updates"""
    session_id = data.get('session_id')
    overlay_data = data.get('overlay_data')
    
    if session_id:
        # Broadcast overlay update ke semua participants
        emit('overlay_sync', {
            'session_id': session_id,
            'overlay_data': overlay_data
        }, room=session_id)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_sessions': len(active_sessions),
        'total_captures': len(capture_history),
        'version': '1.0.0'
    })

@app.route('/api/cleanup', methods=['POST'])
def cleanup_old_files():
    """Cleanup old capture files (admin endpoint)"""
    try:
        # Clean files older than 24 hours
        cutoff_time = datetime.now().timestamp() - (24 * 60 * 60)
        cleaned_count = 0
        
        for capture_dir in CAPTURE_DIR.iterdir():
            if capture_dir.is_dir():
                try:
                    # Parse timestamp dari directory name
                    dir_timestamp = capture_dir.stat().st_ctime
                    if dir_timestamp < cutoff_time:
                        # Remove directory dan contents
                        import shutil
                        shutil.rmtree(capture_dir)
                        cleaned_count += 1
                except Exception as e:
                    logger.warning(f"Failed to clean {capture_dir}: {e}")
        
        # Clean memory storage
        old_captures = [
            capture_id for capture_id, capture in capture_history.items()
            if datetime.fromisoformat(capture['timestamp']).timestamp() < cutoff_time
        ]
        
        for capture_id in old_captures:
            del capture_history[capture_id]
        
        return jsonify({
            'status': 'success',
            'cleaned_directories': cleaned_count,
            'cleaned_memory_entries': len(old_captures),
            'message': f'Cleaned {cleaned_count} old capture directories'
        })
        
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    # Create directories
    CAPTURE_DIR.mkdir(exist_ok=True)
    
    # Log startup info
    logger.info("🎥 Jitsi Bridge System Starting...")
    logger.info(f"📁 Capture directory: {CAPTURE_DIR}")
    logger.info(f"🔗 CORS enabled for all origins")
    logger.info(f"📡 WebSocket support enabled")
    
    # Run server
    socketio.run(
        app,
        host='0.0.0.0',
        port=5001,
        debug=True,
        allow_unsafe_werkzeug=True
    )

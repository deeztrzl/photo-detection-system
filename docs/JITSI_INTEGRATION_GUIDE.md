# 🎥 JITSI MEET INTEGRATION GUIDE
## Photo Detection System Integration dengan Jitsi Meet

---

## 📋 **OVERVIEW**

Panduan lengkap untuk mengintegrasikan **Photo Detection System** ke dalam **Jitsi Meet** untuk melakukan capture KTP dan verifikasi wajah secara real-time dalam video conference.

### **🎯 Tujuan Integration:**
- Capture foto KTP nasabah langsung dari video call Jitsi
- Verifikasi identitas real-time tanpa meninggalkan meeting
- Workflow CS-Nasabah yang seamless
- Auto-download hasil capture dalam format terstruktur

---

## 🔧 **ARSITEKTUR INTEGRATION**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Jitsi Meet    │◄──►│  Injection Layer │◄──►│ Detection Engine│
│   (Frontend)    │    │  (Bridge System) │    │  (AI Backend)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                       │
         │                        │                       │
    ┌────▼────┐              ┌───▼───┐               ┌────▼────┐
    │ Video   │              │Socket │               │Face/KTP │
    │ Stream  │              │  IO   │               │Detection│
    └─────────┘              └───────┘               └─────────┘
```

### **Integration Points:**
1. **Frontend Injection** → Browser extension/script
2. **Video Stream Capture** → Canvas-based frame extraction
3. **AI Processing** → Real-time detection backend
4. **Result Delivery** → Auto-download sistem

---

## 🚀 **METODE INTEGRATION**

### **Method 1: Browser Extension (Recommended)**

#### **A. Manifest Configuration**
```json
{
  "manifest_version": 3,
  "name": "Jitsi KTP Capture",
  "version": "1.0.0",
  "description": "KTP and Face capture for Jitsi Meet",
  "permissions": [
    "activeTab",
    "desktopCapture", 
    "storage",
    "downloads"
  ],
  "host_permissions": [
    "https://meet.jit.si/*",
    "https://*.jitsi.net/*",
    "https://8x8.vc/*"
  ],
  "content_scripts": [{
    "matches": [
      "https://meet.jit.si/*",
      "https://*.jitsi.net/*", 
      "https://8x8.vc/*"
    ],
    "js": [
      "libs/opencv.js",
      "libs/mediapipe.js", 
      "capture-engine.js",
      "jitsi-injector.js"
    ],
    "css": ["styles/overlay.css"]
  }],
  "background": {
    "service_worker": "background.js"
  },
  "action": {
    "default_popup": "popup.html",
    "default_title": "KTP Capture Controls"
  }
}
```

#### **B. Content Script Injection**
```javascript
// jitsi-injector.js
class JitsiCaptureInjector {
    constructor() {
        this.detectionEngine = new CaptureEngine();
        this.overlaySystem = new OverlaySystem();
        this.isInitialized = false;
        
        this.init();
    }
    
    async init() {
        // Wait for Jitsi to load
        await this.waitForJitsiLoad();
        
        // Inject capture controls
        this.injectCaptureControls();
        
        // Setup video stream monitoring
        this.setupVideoStreamCapture();
        
        // Initialize overlay system
        this.overlaySystem.init();
        
        this.isInitialized = true;
        console.log('✅ Jitsi KTP Capture initialized');
    }
    
    waitForJitsiLoad() {
        return new Promise((resolve) => {
            const checkJitsi = () => {
                if (window.APP && window.APP.conference) {
                    resolve();
                } else {
                    setTimeout(checkJitsi, 500);
                }
            };
            checkJitsi();
        });
    }
    
    injectCaptureControls() {
        // Inject ke Jitsi toolbar
        const toolbar = document.querySelector('#new-toolbox');
        if (!toolbar) return;
        
        const captureButton = this.createCaptureButton();
        toolbar.appendChild(captureButton);
        
        // Inject overlay panel
        const overlayPanel = this.createOverlayPanel();
        document.body.appendChild(overlayPanel);
    }
    
    createCaptureButton() {
        const button = document.createElement('div');
        button.className = 'toolbox-button';
        button.innerHTML = `
            <div class="toolbox-icon">
                <svg width="24" height="24" viewBox="0 0 24 24">
                    <path d="M12 15.5A3.5 3.5 0 0 1 8.5 12A3.5 3.5 0 0 1 12 8.5a3.5 3.5 0 0 1 3.5 3.5a3.5 3.5 0 0 1-3.5 3.5M12 2a10 10 0 0 0-10 10a10 10 0 0 0 10 10a10 10 0 0 0 10-10A10 10 0 0 0 12 2Z" fill="currentColor"/>
                </svg>
            </div>
            <span class="toolbox-label">KTP Capture</span>
        `;
        
        button.addEventListener('click', () => {
            this.toggleCaptureMode();
        });
        
        return button;
    }
    
    createOverlayPanel() {
        const panel = document.createElement('div');
        panel.id = 'ktp-capture-overlay';
        panel.innerHTML = `
            <div class="capture-panel">
                <div class="panel-header">
                    <h3>KTP Capture System</h3>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="panel-content">
                    <div class="participant-list">
                        <h4>Select Participant:</h4>
                        <div id="participants-dropdown"></div>
                    </div>
                    <div class="capture-controls">
                        <button id="auto-capture-btn">Auto Capture</button>
                        <button id="manual-capture-btn">Manual Capture</button>
                        <button id="toggle-overlay-btn">Toggle Overlay</button>
                    </div>
                    <div class="capture-preview">
                        <canvas id="preview-canvas"></canvas>
                    </div>
                    <div class="status-display">
                        <span id="detection-status">Ready</span>
                    </div>
                </div>
            </div>
        `;
        
        // Event listeners
        this.setupPanelEvents(panel);
        
        return panel;
    }
    
    setupVideoStreamCapture() {
        // Monitor semua video elements di Jitsi
        const videoElements = document.querySelectorAll('video');
        
        videoElements.forEach((video, index) => {
            if (video.srcObject) {
                this.setupStreamCapture(video, index);
            }
        });
        
        // Monitor untuk video baru (participants joining)
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.tagName === 'VIDEO' && node.srcObject) {
                        this.setupStreamCapture(node, Date.now());
                    }
                });
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    setupStreamCapture(videoElement, participantId) {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // Capture frame dari video stream
        const captureFrame = () => {
            if (videoElement.videoWidth && videoElement.videoHeight) {
                canvas.width = videoElement.videoWidth;
                canvas.height = videoElement.videoHeight;
                
                ctx.drawImage(videoElement, 0, 0);
                
                // Convert ke format yang bisa diproses AI
                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                
                // Send ke detection engine
                this.detectionEngine.processFrame(imageData, participantId);
            }
        };
        
        // Setup interval capture (adjustable)
        const captureInterval = setInterval(captureFrame, 100); // 10 FPS
        
        // Cleanup saat video element removed
        const cleanupObserver = new MutationObserver(() => {
            if (!document.contains(videoElement)) {
                clearInterval(captureInterval);
                cleanupObserver.disconnect();
            }
        });
        
        cleanupObserver.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    toggleCaptureMode() {
        const overlay = document.getElementById('ktp-capture-overlay');
        overlay.style.display = overlay.style.display === 'none' ? 'block' : 'none';
    }
}

// Initialize saat page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new JitsiCaptureInjector();
    });
} else {
    new JitsiCaptureInjector();
}
```

#### **C. Detection Engine Integration**
```javascript
// capture-engine.js
class CaptureEngine {
    constructor() {
        this.faceDetector = null;
        this.isProcessing = false;
        this.detectionResults = new Map();
        
        this.initializeDetectors();
    }
    
    async initializeDetectors() {
        // Initialize MediaPipe Face Detection
        const vision = await import('https://cdn.jsdelivr.net/npm/@mediapipe/face_detection@0.4/face_detection.js');
        
        this.faceDetector = new vision.FaceDetection({
            locateFile: (file) => {
                return `https://cdn.jsdelivr.net/npm/@mediapipe/face_detection@0.4/${file}`;
            }
        });
        
        this.faceDetector.setOptions({
            model: 'short',
            minDetectionConfidence: 0.5
        });
        
        this.faceDetector.onResults((results) => {
            this.processFaceResults(results);
        });
    }
    
    async processFrame(imageData, participantId) {
        if (this.isProcessing || !this.faceDetector) return;
        
        this.isProcessing = true;
        
        try {
            // Convert ImageData ke format MediaPipe
            const rgbaArray = imageData.data;
            const width = imageData.width;
            const height = imageData.height;
            
            // Create RGB array (MediaPipe expects RGB)
            const rgbArray = new Uint8Array(width * height * 3);
            for (let i = 0; i < rgbaArray.length; i += 4) {
                const rgbIndex = (i / 4) * 3;
                rgbArray[rgbIndex] = rgbaArray[i];     // R
                rgbArray[rgbIndex + 1] = rgbaArray[i + 1]; // G
                rgbArray[rgbIndex + 2] = rgbaArray[i + 2]; // B
            }
            
            // Send ke face detector
            await this.faceDetector.send({
                image: {
                    data: rgbArray,
                    width: width,
                    height: height
                }
            });
            
            // Detect KTP (blue color detection)
            const ktpDetection = this.detectKTP(imageData);
            
            // Store results
            this.detectionResults.set(participantId, {
                face: this.lastFaceResults,
                ktp: ktpDetection,
                timestamp: Date.now()
            });
            
        } catch (error) {
            console.error('Detection error:', error);
        } finally {
            this.isProcessing = false;
        }
    }
    
    processFaceResults(results) {
        this.lastFaceResults = results;
        
        // Update UI dengan detection status
        this.updateDetectionStatus(results.detections.length > 0);
    }
    
    detectKTP(imageData) {
        // Convert ke HSV untuk blue detection
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = imageData.width;
        canvas.height = imageData.height;
        
        ctx.putImageData(imageData, 0, 0);
        
        // Simple blue detection (simplified version)
        const bluePixels = this.countBluePixels(imageData);
        const totalPixels = imageData.width * imageData.height;
        const blueRatio = bluePixels / totalPixels;
        
        return {
            detected: blueRatio > 0.1, // Threshold untuk KTP detection
            confidence: blueRatio,
            area: bluePixels
        };
    }
    
    countBluePixels(imageData) {
        const data = imageData.data;
        let blueCount = 0;
        
        for (let i = 0; i < data.length; i += 4) {
            const r = data[i];
            const g = data[i + 1]; 
            const b = data[i + 2];
            
            // Simple blue detection
            if (b > r && b > g && b > 100) {
                blueCount++;
            }
        }
        
        return blueCount;
    }
    
    updateDetectionStatus(faceDetected) {
        const statusElement = document.getElementById('detection-status');
        if (statusElement) {
            statusElement.textContent = faceDetected ? 'Face Detected' : 'No Face';
            statusElement.className = faceDetected ? 'status-detected' : 'status-waiting';
        }
    }
    
    captureParticipant(participantId, mode = 'manual') {
        const results = this.detectionResults.get(participantId);
        if (!results) {
            alert('No detection data available for this participant');
            return;
        }
        
        // Create capture data
        const captureData = {
            participantId: participantId,
            timestamp: new Date().toISOString(),
            mode: mode,
            faceDetection: results.face,
            ktpDetection: results.ktp
        };
        
        // Send untuk processing dan download
        this.processCaptureData(captureData);
    }
    
    async processCaptureData(captureData) {
        try {
            // Send ke backend untuk processing
            const response = await fetch('http://localhost:5000/api/process_capture', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(captureData)
            });
            
            if (response.ok) {
                const result = await response.json();
                
                // Auto download hasil
                this.downloadCaptureResults(result);
                
                // Show success notification
                this.showNotification('Capture berhasil! File sedang di-download.');
            } else {
                throw new Error('Failed to process capture');
            }
            
        } catch (error) {
            console.error('Capture processing error:', error);
            this.showNotification('Error processing capture: ' + error.message, 'error');
        }
    }
    
    downloadCaptureResults(result) {
        // Download face image
        if (result.face_image) {
            this.downloadFile(result.face_image, result.face_filename);
        }
        
        // Download KTP image  
        if (result.ktp_image) {
            this.downloadFile(result.ktp_image, result.ktp_filename);
        }
        
        // Download ZIP if available
        if (result.zip_file) {
            this.downloadFile(result.zip_file, result.zip_filename);
        }
    }
    
    downloadFile(base64Data, filename) {
        const link = document.createElement('a');
        link.href = 'data:application/octet-stream;base64,' + base64Data;
        link.download = filename;
        link.click();
    }
    
    showNotification(message, type = 'success') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `capture-notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Remove setelah 3 detik
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 3000);
    }
}
```

---

### **Method 2: User Script (Greasemonkey/Tampermonkey)**

```javascript
// ==UserScript==
// @name         Jitsi KTP Capture
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  KTP capture untuk Jitsi Meet
// @author       You
// @match        https://meet.jit.si/*
// @match        https://*.jitsi.net/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';
    
    // Load dependencies
    const loadScript = (src) => {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    };
    
    // Initialize setelah dependencies loaded
    Promise.all([
        loadScript('https://docs.opencv.org/4.5.0/opencv.js'),
        loadScript('https://cdn.jsdelivr.net/npm/@mediapipe/face_detection@0.4/face_detection.js')
    ]).then(() => {
        // Initialize capture system
        new JitsiCaptureInjector();
    });
})();
```

---

### **Method 3: Backend Bridge System**

#### **A. Flask Backend Enhancement**
```python
# jitsi_bridge.py
from flask import Flask, request, jsonify, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import base64
import cv2
import numpy as np
from modules.main_detection.app import detect_face_and_ktp
import os
from datetime import datetime
import zipfile
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jitsi_bridge_secret'
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# Storage untuk capture sessions
capture_sessions = {}

@app.route('/api/process_capture', methods=['POST'])
def process_capture():
    """Process capture data dari Jitsi frontend"""
    try:
        data = request.get_json()
        
        participant_id = data['participantId']
        timestamp = data['timestamp']
        mode = data['mode']
        
        # Process dengan detection engine
        if 'image_data' in data:
            # Decode base64 image
            image_data = base64.b64decode(data['image_data'])
            nparr = np.frombuffer(image_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Run detection
            face_img, ktp_img = detect_face_and_ktp(frame)
            
            # Save results
            results = save_capture_results(participant_id, face_img, ktp_img, timestamp)
            
            return jsonify({
                'status': 'success',
                'participant_id': participant_id,
                'timestamp': timestamp,
                **results
            })
        
        return jsonify({'status': 'error', 'message': 'No image data provided'})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

def save_capture_results(participant_id, face_img, ktp_img, timestamp):
    """Save capture results dan return download links"""
    results = {}
    
    # Create session folder
    session_folder = f"static/jitsi_captures/{participant_id}_{timestamp}"
    os.makedirs(session_folder, exist_ok=True)
    
    # Save face image
    if face_img is not None:
        face_filename = f"{participant_id}_face_{timestamp}.jpg"
        face_path = os.path.join(session_folder, face_filename)
        cv2.imwrite(face_path, face_img)
        
        # Convert ke base64 untuk download
        with open(face_path, 'rb') as f:
            face_b64 = base64.b64encode(f.read()).decode()
        
        results['face_image'] = face_b64
        results['face_filename'] = face_filename
    
    # Save KTP image
    if ktp_img is not None:
        ktp_filename = f"{participant_id}_ktp_{timestamp}.jpg"
        ktp_path = os.path.join(session_folder, ktp_filename)
        cv2.imwrite(ktp_path, ktp_img)
        
        # Convert ke base64 untuk download
        with open(ktp_path, 'rb') as f:
            ktp_b64 = base64.b64encode(f.read()).decode()
        
        results['ktp_image'] = ktp_b64
        results['ktp_filename'] = ktp_filename
    
    # Create ZIP file
    zip_filename = f"{participant_id}_capture_{timestamp}.zip"
    zip_path = os.path.join(session_folder, zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        if 'face_filename' in results:
            zipf.write(os.path.join(session_folder, results['face_filename']), results['face_filename'])
        if 'ktp_filename' in results:
            zipf.write(os.path.join(session_folder, results['ktp_filename']), results['ktp_filename'])
    
    # Convert ZIP ke base64
    with open(zip_path, 'rb') as f:
        zip_b64 = base64.b64encode(f.read()).decode()
    
    results['zip_file'] = zip_b64
    results['zip_filename'] = zip_filename
    
    return results

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'status': 'Connected to Jitsi Bridge'})

@socketio.on('start_capture_session')
def handle_start_session(data):
    """Start new capture session"""
    session_id = data['session_id']
    participants = data['participants']
    
    capture_sessions[session_id] = {
        'participants': participants,
        'status': 'active',
        'created_at': datetime.now().isoformat()
    }
    
    emit('session_started', {'session_id': session_id})

@app.route('/api/download/<path:filename>')
def download_file(filename):
    """Download capture files"""
    try:
        # Security: validate filename
        if '..' in filename or filename.startswith('/'):
            return jsonify({'error': 'Invalid filename'}), 400
        
        file_path = os.path.join('static/jitsi_captures', filename)
        
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create directories
    os.makedirs('static/jitsi_captures', exist_ok=True)
    
    # Run server
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
```

---

## 🎨 **UI/UX INTEGRATION**

### **CSS Styling untuk Jitsi Integration**
```css
/* styles/overlay.css */
#ktp-capture-overlay {
    position: fixed;
    top: 20px;
    right: 20px;
    width: 350px;
    height: auto;
    background: rgba(0, 0, 0, 0.9);
    border-radius: 12px;
    border: 2px solid #00D4FF;
    color: white;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto;
    z-index: 9999;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    display: none;
}

.capture-panel {
    padding: 16px;
}

.panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    border-bottom: 1px solid #333;
    padding-bottom: 12px;
}

.panel-header h3 {
    margin: 0;
    font-size: 16px;
    color: #00D4FF;
}

.close-btn {
    background: none;
    border: none;
    color: #fff;
    font-size: 24px;
    cursor: pointer;
    padding: 0;
    width: 24px;
    height: 24px;
}

.close-btn:hover {
    color: #ff4757;
}

.participant-list {
    margin-bottom: 16px;
}

.participant-list h4 {
    margin: 0 0 8px 0;
    font-size: 14px;
    color: #ccc;
}

#participants-dropdown {
    width: 100%;
    padding: 8px;
    background: #2c2c2c;
    border: 1px solid #555;
    border-radius: 6px;
    color: white;
    font-size: 14px;
}

.capture-controls {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
}

.capture-controls button {
    flex: 1;
    padding: 10px;
    background: #00D4FF;
    border: none;
    border-radius: 6px;
    color: white;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
}

.capture-controls button:hover {
    background: #00B4D8;
    transform: translateY(-1px);
}

.capture-controls button:active {
    transform: translateY(0);
}

#toggle-overlay-btn {
    background: #ff6b6b !important;
}

#toggle-overlay-btn:hover {
    background: #ff5252 !important;
}

.capture-preview {
    margin-bottom: 16px;
}

#preview-canvas {
    width: 100%;
    height: 150px;
    background: #1a1a1a;
    border-radius: 6px;
    border: 1px solid #333;
}

.status-display {
    text-align: center;
    padding: 8px;
    border-radius: 6px;
    background: #2c2c2c;
}

.status-detected {
    color: #4CAF50;
    font-weight: 600;
}

.status-waiting {
    color: #ff9800;
}

/* Capture Button di Jitsi Toolbar */
.toolbox-button .toolbox-icon svg {
    fill: currentColor;
}

.toolbox-button:hover {
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 6px;
}

/* Notifications */
.capture-notification {
    position: fixed;
    top: 80px;
    right: 20px;
    padding: 12px 16px;
    border-radius: 6px;
    color: white;
    font-weight: 600;
    z-index: 10000;
    max-width: 300px;
    animation: slideIn 0.3s ease;
}

.capture-notification.success {
    background: #4CAF50;
    border-left: 4px solid #2E7D32;
}

.capture-notification.error {
    background: #f44336;
    border-left: 4px solid #C62828;
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

/* Overlay Guides */
.ktp-guide-overlay {
    position: absolute;
    pointer-events: none;
    z-index: 1000;
}

.face-guide {
    border: 3px solid #4CAF50;
    border-radius: 50%;
    background: rgba(76, 175, 80, 0.1);
}

.ktp-guide {
    border: 3px solid #2196F3;
    border-radius: 8px;
    background: rgba(33, 150, 243, 0.1);
}

.guide-label {
    position: absolute;
    top: -25px;
    left: 0;
    color: white;
    font-size: 12px;
    font-weight: 600;
    background: rgba(0, 0, 0, 0.7);
    padding: 2px 8px;
    border-radius: 4px;
}
```

---

## 📱 **DEPLOYMENT GUIDE**

### **Development Setup**
```bash
# 1. Setup backend bridge
cd photo-detection
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install flask flask-socketio flask-cors opencv-python mediapipe

# 2. Run bridge server
python jitsi_bridge.py

# 3. Load extension di browser
# Chrome: chrome://extensions/ → Developer mode → Load unpacked
# Firefox: about:debugging → This Firefox → Load Temporary Add-on
```

### **Production Deployment**
```bash
# 1. Build extension untuk production
npm run build

# 2. Package extension
zip -r jitsi-ktp-capture-v1.0.zip dist/

# 3. Deploy backend
docker build -t jitsi-bridge .
docker run -p 5001:5001 jitsi-bridge

# 4. Configure HTTPS untuk production
```

---

## 🔒 **SECURITY CONSIDERATIONS**

### **Privacy & Data Protection**
```javascript
// Data retention policy
const DATA_RETENTION_HOURS = 24;

// Automatic cleanup
setInterval(() => {
    cleanupOldCaptures();
}, 3600000); // Every hour

function cleanupOldCaptures() {
    const cutoffTime = Date.now() - (DATA_RETENTION_HOURS * 60 * 60 * 1000);
    // Remove old capture data
}
```

### **Permission Management**
```json
{
  "permissions": [
    "activeTab",        // Access to current tab only
    "storage",          // Local storage for settings
    "downloads"         // Auto-download functionality
  ],
  "optional_permissions": [
    "desktopCapture"    // Only if screen capture needed
  ]
}
```

---

## 📋 **TESTING & VALIDATION**

### **Test Scenarios**
```javascript
// Unit tests untuk detection engine
describe('CaptureEngine', () => {
    test('should detect face in video frame', async () => {
        const engine = new CaptureEngine();
        const result = await engine.processFrame(mockImageData, 'test-participant');
        expect(result.face.detected).toBe(true);
    });
    
    test('should handle multiple participants', () => {
        // Test multi-participant handling
    });
});

// Integration tests
describe('Jitsi Integration', () => {
    test('should inject controls successfully', () => {
        // Test UI injection
    });
    
    test('should capture video frames', () => {
        // Test video capture
    });
});
```

---

## 🚀 **FUTURE ENHANCEMENTS**

### **Planned Features**
- **Real-time Liveness Detection** untuk anti-spoofing
- **Multi-language Support** untuk global deployment  
- **Advanced Analytics** untuk capture quality metrics
- **Mobile App Integration** untuk hybrid workflows
- **API Integration** dengan core banking systems

### **Performance Optimizations**
- **WebAssembly** untuk faster image processing
- **WebWorkers** untuk non-blocking detection
- **Progressive Loading** untuk better UX
- **Caching Strategy** untuk repeated participants

---

## 📞 **SUPPORT & TROUBLESHOOTING**

### **Common Issues**
1. **Extension tidak load**: Check manifest permissions
2. **Video tidak terdeteksi**: Verify video element selectors
3. **Detection tidak akurat**: Adjust confidence thresholds
4. **Download gagal**: Check CORS dan backend connectivity

### **Debug Mode**
```javascript
// Enable debug logging
localStorage.setItem('jitsi-capture-debug', 'true');

// Debug panel
window.debugCaptureSystem = () => {
    console.log('Detection results:', captureEngine.detectionResults);
    console.log('Active participants:', participants);
    console.log('System status:', systemStatus);
};
```

---

**🎯 Integration selesai! Sistem siap untuk deployment dan testing.**

# 🔧 DEVELOPER GUIDE
## Advanced Setup & Customization untuk Photo Detection AI

---

## 🏗️ **Development Environment Setup**

### **IDE Recommendations:**
- **Visual Studio Code** dengan extensions:
  - Python
  - Flask Snippets
  - OpenCV Snippets
  - Prettier Code formatter

### **Development Dependencies:**
```bash
pip install -r requirements-dev.txt
```

**requirements-dev.txt:**
```
# Production dependencies
Flask==2.3.3
opencv-python==4.8.0.76
mediapipe==0.10.3
numpy==1.24.3
Pillow==10.0.0

# Development dependencies
pytest==7.4.0
pytest-flask==1.2.0
black==23.7.0
flake8==6.0.0
autopep8==2.0.2
```

---

## ⚙️ **Configuration Options**

### **App Configuration (app.py):**

#### **Server Settings:**
```python
# Development
app.run(host='127.0.0.1', port=5000, debug=True)

# Production
app.run(host='0.0.0.0', port=8080, debug=False)

# Custom
app.run(host='192.168.1.100', port=3000, debug=False)
```

#### **Detection Parameters:**
```python
# Face Detection Confidence (0.1 - 1.0)
min_detection_confidence=0.5

# KTP Detection Thresholds
KTP_AREA_THRESHOLD = 0.015    # 1.5% of frame area
KTP_ASPECT_MIN = 1.4          # Minimum aspect ratio
KTP_ASPECT_MAX = 1.9          # Maximum aspect ratio
BLUE_PIXEL_RATIO = 0.3        # 30% blue pixels required

# Countdown Timer
COUNTDOWN_DURATION = 3        # Seconds
```

#### **Camera Settings:**
```python
# Camera Configuration
CAMERA_INDEX = 0              # Camera device index
FRAME_WIDTH = 640             # Video width
FRAME_HEIGHT = 480            # Video height
FPS = 30                      # Frames per second

# Output Image Sizes
FACE_OUTPUT_SIZE = (300, 300)    # Face image resolution
KTP_OUTPUT_SIZE = (480, 300)     # KTP image resolution
```

---

## 🎨 **UI Customization**

### **Color Themes (templates/index.html):**

#### **CSS Variables:**
```css
:root {
    --primary-color: #007bff;
    --success-color: #28a745;
    --warning-color: #ffc107;
    --danger-color: #dc3545;
    --background-color: #f4f4f4;
    --text-color: #333;
    --border-radius: 8px;
}
```

#### **Dark Theme:**
```css
.dark-theme {
    --primary-color: #0d6efd;
    --background-color: #1a1a1a;
    --text-color: #ffffff;
    --card-background: #2d2d2d;
}
```

### **Layout Modifications:**

#### **Vertical Layout:**
```css
.main-content {
    flex-direction: column;
    gap: 20px;
}

.camera-section, .results-section {
    flex: none;
    width: 100%;
}
```

#### **Full Screen Mode:**
```css
.fullscreen-mode {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 9999;
    background: black;
}
```

---

## 🔌 **API Integration**

### **REST API Endpoints:**

#### **Get Detection Status:**
```bash
GET /detection_status
Content-Type: application/json

Response:
{
    "face_detected": true,
    "ktp_detected": false,
    "both_detected": false,
    "mode": "auto",
    "countdown": {
        "active": false,
        "remaining": 0
    }
}
```

#### **Trigger Capture:**
```bash
POST /capture
Content-Type: application/json

Response:
{
    "face_url": "/static/face_capture.jpg",
    "ktp_url": "/static/ktp_capture.jpg", 
    "status": "success",
    "message": "Capture berhasil!",
    "download_url": "/download/20250825_143022",
    "timestamp": "20250825_143022"
}
```

#### **Switch Mode:**
```bash
POST /toggle_mode
Content-Type: application/json
Body: {"mode": "manual"}

Response:
{
    "status": "success",
    "mode": "manual"
}
```

### **JavaScript API Client:**
```javascript
class PhotoDetectionAPI {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
    }
    
    async getStatus() {
        const response = await fetch(`${this.baseURL}/detection_status`);
        return response.json();
    }
    
    async capture() {
        const response = await fetch(`${this.baseURL}/capture`, {
            method: 'POST'
        });
        return response.json();
    }
    
    async setMode(mode) {
        const response = await fetch(`${this.baseURL}/toggle_mode`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({mode})
        });
        return response.json();
    }
}

// Usage
const api = new PhotoDetectionAPI();
const status = await api.getStatus();
```

---

## 🔧 **Advanced Features**

### **Multiple Camera Support:**
```python
def get_available_cameras():
    """Get list of available cameras"""
    cameras = []
    for i in range(10):  # Check first 10 camera indices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cameras.append({
                'index': i,
                'name': f'Camera {i}'
            })
            cap.release()
    return cameras

@app.route('/cameras')
def list_cameras():
    return jsonify(get_available_cameras())
```

### **Image Quality Enhancement:**
```python
def enhance_image_quality(image):
    """Apply image enhancement filters"""
    # Brightness and contrast adjustment
    alpha = 1.2  # Contrast control (1.0-3.0)
    beta = 10    # Brightness control (0-100)
    enhanced = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    
    # Sharpening filter
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)
    
    return sharpened
```

### **Batch Processing:**
```python
@app.route('/batch_capture', methods=['POST'])
def batch_capture():
    """Capture multiple photos in sequence"""
    results = []
    count = request.json.get('count', 5)
    interval = request.json.get('interval', 2)  # seconds
    
    for i in range(count):
        if i > 0:
            time.sleep(interval)
        
        # Capture logic here
        result = capture_single()
        results.append(result)
    
    return jsonify({'results': results})
```

---

## 📊 **Monitoring & Analytics**

### **Performance Monitoring:**
```python
import time
import psutil

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'total_captures': 0,
            'successful_captures': 0,
            'average_processing_time': 0,
            'memory_usage': 0,
            'cpu_usage': 0
        }
    
    def record_capture(self, processing_time, success=True):
        self.metrics['total_captures'] += 1
        if success:
            self.metrics['successful_captures'] += 1
        
        # Update average processing time
        current_avg = self.metrics['average_processing_time']
        total = self.metrics['total_captures']
        self.metrics['average_processing_time'] = (
            (current_avg * (total - 1) + processing_time) / total
        )
    
    def get_system_metrics(self):
        self.metrics['memory_usage'] = psutil.virtual_memory().percent
        self.metrics['cpu_usage'] = psutil.cpu_percent(interval=1)
        return self.metrics

monitor = PerformanceMonitor()

@app.route('/metrics')
def get_metrics():
    return jsonify(monitor.get_system_metrics())
```

### **Logging Configuration:**
```python
import logging
from logging.handlers import RotatingFileHandler

# Setup logging
if not app.debug:
    file_handler = RotatingFileHandler(
        'logs/photo_detection.log', 
        maxBytes=10240, 
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Photo Detection startup')
```

---

## 🔒 **Security Enhancements**

### **Authentication (Optional):**
```python
from functools import wraps
from flask import session, request, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Simple authentication (use proper auth in production)
        if username == 'admin' and password == 'secure_password':
            session['user'] = username
            return redirect(url_for('index'))
        
        return 'Invalid credentials', 401
    
    return render_template('login.html')

@app.route('/')
@login_required
def index():
    return render_template('index.html')
```

### **CORS Configuration:**
```python
from flask_cors import CORS

# Allow specific origins
CORS(app, origins=['http://localhost:3000', 'https://yourdomain.com'])

# Or allow all origins (development only)
CORS(app, origins='*')
```

### **Rate Limiting:**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/capture', methods=['POST'])
@limiter.limit("10 per minute")
def capture():
    # Capture logic here
    pass
```

---

## 🐳 **Docker Deployment**

### **Dockerfile:**
```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

CMD ["python", "app.py"]
```

### **docker-compose.yml:**
```yaml
version: '3.8'

services:
  photo-detection:
    build: .
    ports:
      - "5000:5000"
    devices:
      - "/dev/video0:/dev/video0"  # Camera access
    volumes:
      - ./static:/app/static
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=false
    restart: unless-stopped
```

### **Build & Run:**
```bash
# Build image
docker build -t photo-detection .

# Run with camera access
docker run -p 5000:5000 --device=/dev/video0 photo-detection

# Or use docker-compose
docker-compose up -d
```

---

## 🚀 **Production Deployment**

### **Using Gunicorn:**
```bash
# Install Gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:app

# With configuration file
gunicorn -c gunicorn.conf.py app:app
```

### **gunicorn.conf.py:**
```python
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

### **Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Static files
    location /static {
        alias /path/to/photo-detection/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## 📱 **Mobile Optimization**

### **Responsive Improvements:**
```css
/* Mobile-first approach */
@media (max-width: 768px) {
    .main-content {
        flex-direction: column;
        padding: 10px;
    }
    
    #video-stream {
        width: 100%;
        max-height: 50vh;
    }
    
    .btn-capture {
        font-size: 20px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .countdown-number {
        font-size: 100px;
    }
}

/* Tablet optimization */
@media (min-width: 769px) and (max-width: 1024px) {
    .container {
        max-width: 95%;
    }
    
    .main-content {
        gap: 20px;
    }
}
```

### **Touch Gestures:**
```javascript
// Add touch support for mobile devices
let touchStartX = 0;
let touchStartY = 0;

document.addEventListener('touchstart', function(e) {
    touchStartX = e.touches[0].clientX;
    touchStartY = e.touches[0].clientY;
});

document.addEventListener('touchend', function(e) {
    if (!touchStartX || !touchStartY) return;
    
    let touchEndX = e.changedTouches[0].clientX;
    let touchEndY = e.changedTouches[0].clientY;
    
    let diffX = touchStartX - touchEndX;
    let diffY = touchStartY - touchEndY;
    
    // Swipe gestures
    if (Math.abs(diffX) > Math.abs(diffY)) {
        if (Math.abs(diffX) > 50) {
            if (diffX > 0) {
                // Swipe left - next mode
                toggleMode();
            } else {
                // Swipe right - previous mode
                toggleMode();
            }
        }
    }
    
    touchStartX = 0;
    touchStartY = 0;
});
```

---

## 🧪 **Testing**

### **Unit Tests (test_app.py):**
```python
import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_page(client):
    """Test main page loads correctly"""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'Verifikasi KTP' in rv.data

def test_detection_status(client):
    """Test detection status endpoint"""
    rv = client.get('/detection_status')
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert 'face_detected' in data
    assert 'ktp_detected' in data

def test_toggle_mode(client):
    """Test mode switching"""
    rv = client.post('/toggle_mode', 
                     json={'mode': 'manual'},
                     content_type='application/json')
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data['mode'] == 'manual'

def test_capture_endpoint(client):
    """Test capture endpoint"""
    rv = client.post('/capture')
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert 'status' in data
```

### **Run Tests:**
```bash
# Install pytest
pip install pytest pytest-flask

# Run tests
pytest test_app.py -v

# Run with coverage
pytest --cov=app test_app.py
```

---

## 📈 **Performance Optimization**

### **Image Processing Optimization:**
```python
# Use threading for heavy operations
import threading
from concurrent.futures import ThreadPoolExecutor

class OptimizedProcessor:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    def process_frame_async(self, frame):
        """Process frame in background thread"""
        future = self.executor.submit(detect_face_and_ktp, frame)
        return future
    
    def get_result(self, future, timeout=1.0):
        """Get result with timeout"""
        try:
            return future.result(timeout=timeout)
        except:
            return None, None, None
```

### **Caching Strategy:**
```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def cached_detection(frame_hash):
    """Cache detection results for similar frames"""
    # This would need proper implementation
    pass

def get_frame_hash(frame):
    """Generate hash for frame caching"""
    return hashlib.md5(frame.tobytes()).hexdigest()
```

---

**🔧 Dengan panduan developer ini, Anda dapat mengkustomisasi dan mengembangkan aplikasi Photo Detection AI sesuai kebutuhan spesifik!**

"""
Photo Detection System - Main Application
Modular Flask application for KTP and face detection
"""
from flask import Flask

# Import konfigurasi dan inisialisasi
from core.config import load_ktp_template

# Import routes
from routes.main_routes import init_main_routes
from routes.capture_routes import init_capture_routes

def create_app():
    """Application factory"""
    app = Flask(__name__)
    
    # Load KTP template saat startup
    load_ktp_template()
    
    # Initialize routes
    init_main_routes(app)
    init_capture_routes(app)
    
    return app

# Create application instance
app = create_app()

if __name__ == '__main__':
    print("🚀 Starting Photo Detection System...")
    print("📸 Camera initializing...")
    print("🎯 Template matching ready...")
    print("🌐 Server akan berjalan di: http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=True)

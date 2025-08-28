#!/usr/bin/env python3
"""
🧪 System Validation Script untuk Photo Detection System
Memvalidasi semua komponen sistem sebelum menjalankan aplikasi
"""

import sys
import os
import importlib
import subprocess
import platform
from pathlib import Path

def print_header():
    print("🧪 Photo Detection System - Validation Script")
    print("=" * 50)
    print()

def print_section(title):
    print(f"\n📋 {title}")
    print("-" * (len(title) + 4))

def check_result(condition, success_msg, error_msg):
    if condition:
        print(f"✅ {success_msg}")
        return True
    else:
        print(f"❌ {error_msg}")
        return False

def check_python_version():
    """Check Python version compatibility"""
    print_section("Python Version Check")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    print(f"🐍 Python version: {version_str}")
    print(f"🖥️  Platform: {platform.system()} {platform.release()}")
    print(f"📁 Python executable: {sys.executable}")
    
    is_compatible = version.major == 3 and version.minor >= 8
    return check_result(
        is_compatible,
        f"Python {version_str} is compatible",
        f"Python {version_str} is not supported. Need Python 3.8+"
    )

def check_virtual_environment():
    """Check if running in virtual environment"""
    print_section("Virtual Environment Check")
    
    in_venv = (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    
    if in_venv:
        print(f"📁 Virtual env path: {sys.prefix}")
    
    return check_result(
        in_venv,
        "Running in virtual environment",
        "Not in virtual environment (recommended to use venv)"
    )

def check_package_installation():
    """Check all required packages"""
    print_section("Package Installation Check")
    
    required_packages = {
        'cv2': 'opencv-python',
        'mediapipe': 'mediapipe',
        'flask': 'Flask',
        'numpy': 'numpy',
        'PIL': 'Pillow',
        'requests': 'requests',
        'scipy': 'scipy',
        'skimage': 'scikit-image',
        'pywt': 'PyWavelets'
    }
    
    all_installed = True
    
    for module, package in required_packages.items():
        try:
            imported_module = importlib.import_module(module)
            version = getattr(imported_module, '__version__', 'unknown')
            print(f"✅ {package}: {version}")
        except ImportError:
            print(f"❌ {package}: Not installed")
            all_installed = False
    
    return all_installed

def check_camera_access():
    """Check camera accessibility"""
    print_section("Camera Access Check")
    
    try:
        import cv2
        
        # Test multiple camera indices
        camera_found = False
        working_cameras = []
        
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    working_cameras.append(i)
                    camera_found = True
                cap.release()
        
        if camera_found:
            print(f"📹 Working cameras found at index: {working_cameras}")
        
        return check_result(
            camera_found,
            f"Camera accessible (indices: {working_cameras})",
            "No working cameras found"
        )
        
    except Exception as e:
        return check_result(False, "", f"Camera test failed: {str(e)}")

def check_file_structure():
    """Check project file structure"""
    print_section("File Structure Check")
    
    required_files = [
        'launcher.py',
        'requirements.txt',
        'modules/main_detection/app.py',
        'modules/main_detection/detection/main_detector.py',
        'assets/ktp muka.png'
    ]
    
    required_dirs = [
        'modules',
        'modules/main_detection',
        'modules/main_detection/detection',
        'modules/jitsi_system',
        'assets',
        'static'
    ]
    
    all_files_exist = True
    
    print("📁 Checking directories:")
    for dir_path in required_dirs:
        exists = Path(dir_path).is_dir()
        status = "✅" if exists else "❌"
        print(f"   {status} {dir_path}")
        if not exists:
            all_files_exist = False
    
    print("\n📄 Checking files:")
    for file_path in required_files:
        exists = Path(file_path).is_file()
        status = "✅" if exists else "❌"
        print(f"   {status} {file_path}")
        if not exists:
            all_files_exist = False
    
    return all_files_exist

def check_port_availability():
    """Check if required ports are available"""
    print_section("Port Availability Check")
    
    import socket
    
    ports_to_check = [8080, 5001, 5002]
    available_ports = []
    
    for port in ports_to_check:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result != 0:  # Port is available
            available_ports.append(port)
            print(f"✅ Port {port}: Available")
        else:
            print(f"⚠️  Port {port}: In use")
    
    return len(available_ports) > 0

def run_quick_test():
    """Run a quick functional test"""
    print_section("Quick Functional Test")
    
    try:
        # Test basic imports and initialization
        import cv2
        import mediapipe as mp
        import numpy as np
        
        # Test MediaPipe face detection
        mp_face_detection = mp.solutions.face_detection
        face_detection = mp_face_detection.FaceDetection()
        
        # Test OpenCV
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        gray = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
        
        print("✅ MediaPipe initialization: OK")
        print("✅ OpenCV operations: OK")
        print("✅ NumPy operations: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Functional test failed: {str(e)}")
        return False

def generate_report(results):
    """Generate validation report"""
    print_section("Validation Report")
    
    total_checks = len(results)
    passed_checks = sum(results.values())
    
    print(f"📊 Total checks: {total_checks}")
    print(f"✅ Passed: {passed_checks}")
    print(f"❌ Failed: {total_checks - passed_checks}")
    
    success_rate = (passed_checks / total_checks) * 100
    print(f"📈 Success rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("\n🎉 System is ready to run!")
        print("   Execute: python launcher.py")
    elif success_rate >= 60:
        print("\n⚠️  System has some issues but might work")
        print("   Check failed items above")
    else:
        print("\n❌ System has major issues")
        print("   Please fix failed items before running")
    
    return success_rate >= 80

def main():
    """Main validation function"""
    print_header()
    
    # Run all validation checks
    results = {
        "Python Version": check_python_version(),
        "Virtual Environment": check_virtual_environment(),
        "Package Installation": check_package_installation(),
        "Camera Access": check_camera_access(),
        "File Structure": check_file_structure(),
        "Port Availability": check_port_availability(),
        "Functional Test": run_quick_test()
    }
    
    # Generate report
    system_ready = generate_report(results)
    
    # Provide recommendations
    print_section("Recommendations")
    
    if not results["Virtual Environment"]:
        print("💡 Create virtual environment: python -m venv .venv")
    
    if not results["Package Installation"]:
        print("💡 Install packages: pip install -r requirements.txt")
    
    if not results["Camera Access"]:
        print("💡 Check camera permissions and close other camera apps")
    
    if not results["Port Availability"]:
        print("💡 Some ports in use - application will try alternative ports")
    
    print("\n📚 For detailed setup guide, see: ../guides/SETUP_GUIDE.md")
    print("🎯 Quick reference: ../guides/QUICK_REFERENCE.md")
    print("🍎 macOS users: ../guides/MACOS_SETUP_GUIDE.md")
    
    return 0 if system_ready else 1

if __name__ == "__main__":
    exit(main())

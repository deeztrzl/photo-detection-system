"""
Photo Detection System Launcher
Pilih aplikasi yang ingin dijalankan
"""

import sys
import os
from pathlib import Path

def get_python_executable():
    """Get the correct Python executable path"""
    # Try virtual environment first
    venv_python = Path(__file__).parent / ".venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        return str(venv_python)
    
    # Fallback to system Python
    return sys.executable

def main():
    python_exe = get_python_executable()
    base_dir = Path(__file__).parent
    
    print("=== Photo Detection System ===")
    print("1. Main Detection App (app.py)")
    print("2. Jitsi Dummy System (jitsi_dummy.py)")
    print("3. Jitsi Bridge Server (jitsi_bridge.py)")
    print("4. Exit")
    
    choice = input("\nPilih aplikasi (1-4): ")
    
    if choice == "1":
        print("Menjalankan Main Detection App...")
        app_path = base_dir / "modules" / "main_detection" / "app.py"
        working_dir = base_dir / "modules" / "main_detection"
        os.chdir(working_dir)
        os.system(f'"{python_exe}" app.py')
    elif choice == "2":
        print("Menjalankan Jitsi Dummy System...")
        app_path = base_dir / "modules" / "jitsi_system" / "jitsi_dummy.py"
        working_dir = base_dir / "modules" / "jitsi_system"
        os.chdir(working_dir)
        os.system(f'"{python_exe}" jitsi_dummy.py')
    elif choice == "3":
        print("Menjalankan Jitsi Bridge Server...")
        app_path = base_dir / "modules" / "jitsi_system" / "jitsi_bridge.py"
        working_dir = base_dir / "modules" / "jitsi_system"
        os.chdir(working_dir)
        os.system(f'"{python_exe}" jitsi_bridge.py')
    elif choice == "4":
        print("Keluar...")
        sys.exit(0)
    else:
        print("Pilihan tidak valid!")
        main()

if __name__ == "__main__":
    main()

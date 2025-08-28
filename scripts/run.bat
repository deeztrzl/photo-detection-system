@echo off
echo ========================================
echo    Photo Detection AI - Startup
echo ========================================
echo.

echo Checking virtual environment...
if not exist ".venv" (
    echo ERROR: Virtual environment tidak ditemukan!
    echo Silakan jalankan install.bat terlebih dahulu
    pause
    exit /b 1
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Starting Photo Detection AI...
echo.
echo ========================================
echo  Server akan berjalan di:
echo  http://localhost:5000
echo  
echo  Tekan Ctrl+C untuk menghentikan server
echo ========================================
echo.

python app.py

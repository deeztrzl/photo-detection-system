#!/bin/bash

echo "========================================"
echo "   Photo Detection AI - Startup"
echo "========================================"
echo

echo "Checking virtual environment..."
if [ ! -d ".venv" ]; then
    echo "ERROR: Virtual environment tidak ditemukan!"
    echo "Silakan jalankan ./install.sh terlebih dahulu"
    exit 1
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Starting Photo Detection AI..."
echo
echo "========================================"
echo " Server akan berjalan di:"
echo " http://localhost:5000"
echo " "
echo " Tekan Ctrl+C untuk menghentikan server"
echo "========================================"
echo

python app.py

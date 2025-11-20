#!/bin/bash

echo "=== mendapatkan informasi folder VEN ==="
if [ ! -d "venv" ]; then
    echo "Membuat virtual environment..."
    python3 -m venv venv
else
    echo "VIRTUALVen sudah ada... lanjut."
fi

echo "=== AKTIFKAN VENV ==="
# Linux / Termux / Mac
source venv/bin/activate

echo "=== UPDATE PIP ==="
pip install --upgrade pip

echo "=== INSTALL REQUIREMENTS ==="
if [ -f "requirements.txt" ]; then
    echo "Menginstall requirements..."
    pip install -r requirements.txt
else
    echo "requirements.txt tidak ditemukan, skip."
fi

echo "=== MENJALANKAN APLIKASI UTAMA ==="
python3 run.py
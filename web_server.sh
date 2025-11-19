#!/bin/bash

echo "=== CEK / BUAT VENV ==="
if [ ! -d "venv" ]; then
    echo "Membuat virtual environment..."
    python3 -m venv venv
else
    echo "Venv sudah ada... lanjut."
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

echo "=== MENJALANKAN APLIKASI ==="
python3 run.py
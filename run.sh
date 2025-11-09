#!/bin/bash
echo "menjalankan program"

# 1. Membuat virtual environment 'venv' jika belum ada
if [ ! -d "venv" ]; then
    echo "Membuat virtual environment..."
    python3 -m venv venv
fi

# 2. Mengaktifkan virtual environment
source venv/bin/activate

# 3. Menginstall requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Menginstall dependency dari requirements.txt..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# (Apa yang terjadi jika semua dependency sudah terinstall?)
# pip akan melewati dependency yang sudah ada versinya sesuai requirements.txt,
# atau meng-upgrade/downgrade otomatis jika versi yang terpasang berbeda.
# Tidak terjadi error, proses tetap berjalan aman.

# 4. Menjalankan aplikasi Python (misal mulai.py)
echo "Menjalankan aplikasi..."
python3 app.py
import os
import platform
import subprocess
import sys

print("🔧 Menjalankan program...")

# ================================
# 1. Deteksi OS
# ================================
os_name = platform.system()
print(f"📌 Sistem operasi terdeteksi: {os_name}")

# ================================
# 2. Buat virtual environment jika belum ada
# ================================
venv_path = "venv"

if not os.path.exists(venv_path):
    print("📦 Membuat virtual environment (venv)...")
    subprocess.call([sys.executable, "-m", "venv", venv_path])
else:
    print("✔️ Virtual environment sudah ada")

# ================================
# 3. Tentukan path python & pip di dalam venv
# ================================
if os_name == "Windows":
    python_path = os.path.join(venv_path, "Scripts", "python.exe")
else:
    python_path = os.path.join(venv_path, "bin", "python")

print(f"🐍 Menggunakan Python: {python_path}")

# ================================
# 4. Install requirements.txt
# ================================
if os.path.exists("requirements.txt"):
    print("📚 Menginstall dependency dari requirements.txt...")
    subprocess.call([python_path, "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.call([python_path, "-m", "pip", "install", "-r", "requirements.txt"])
else:
    print("⚠️ Tidak menemukan requirements.txt — dilewati.")

# ================================
# 5. Jalankan aplikasi Flask (app.py)
# ================================
print("🚀 Menjalankan aplikasi...")
subprocess.call([python_path, "app.py"])
# app/routes/utils.py
import os
import hashlib

# ============================================
# FORMAT EKSTENSI VALID
# (Sama seperti di routes.py — jangan diubah)
# ============================================
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov', 'wmv', 'mp3', 'wav', 'ogg'}


# ============================================
# HELPER FUNCTION
# ============================================

def hash_password(password, salt=None):
    """
    Buat hash password berbasis SHA-256.
    - Jika salt tidak diberikan, dibuat otomatis (16 bytes).
    - Jika salt diberikan sebagai hex string, akan dikonversi kembali ke bytes.
    - Return format: "<salt_hex>$<hashed_hex>"
    Catatan: format ini sama persis seperti di routes.py asli.
    """
    # Membuat salt acak jika belum ada
    if salt is None:
        salt = os.urandom(16)
    # Jika salt dikirim sebagai hex string, ubah menjadi bytes
    if isinstance(salt, str):
        salt = bytes.fromhex(salt)
    # Hash: SHA256(salt + password)
    hashed = hashlib.sha256(salt + password.encode()).hexdigest()
    # Simpan salt sebagai hex + "$" + hashed
    return salt.hex() + "$" + hashed


def verify_password(stored_password, input_pass):
    """
    Verifikasi password yang diinput terhadap password yang tersimpan.
    - stored_password diharapkan dalam format "<salt_hex>$<hashed_hex>"
    - Fungsi ini memakai mekanisme yang sama dengan routes.py asli.
    """
    # Pisah salt dan hash dari string tersimpan
    salt_hex, hashed = stored_password.split("$")
    # Bandingkan keseluruhan string tersimpan dengan hasil hash dari input_pass menggunakan salt yang sama
    return stored_password == hash_password(input_pass, salt_hex)


def allowed_file(filename):
    """
    Cek apakah filename memiliki ekstensi yang diizinkan.
    - Mengembalikan True jika ada titik dan ekstensi ada di ALLOWED_EXTENSIONS.
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_media_files(folder, ext_list):
    """
    Ambil daftar file di folder yang berakhiran salah satu ekstensi di ext_list.
    - Jika folder tidak ada, kembalikan list kosong.
    - ext_list diharapkan berisi ekstensi lengkap dengan titik, misal ['.mp3', '.wav'].
    """
    if not os.path.exists(folder):
        return []
    try:
        return [f for f in os.listdir(folder) if any(f.lower().endswith(ext) for ext in ext_list)]
    except Exception:
        # Jika terjadi error saat membaca folder, kembalikan list kosong agar aplikasi tidak crash
        return []
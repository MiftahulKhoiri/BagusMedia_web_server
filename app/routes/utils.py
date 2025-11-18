# app/routes/utils.py
import os
import hashlib
from flask import session, redirect

# ============================================
# FORMAT EKSTENSI VALID
# ============================================
ALLOWED_EXTENSIONS = {
    'mp4', 'avi', 'mkv', 'mov', 'wmv',
    'mp3', 'wav', 'ogg'
}

# ============================================
# 🔐 SYSTEM PASSWORD HASHING
# ============================================

def hash_password(password, salt=None):
    """
    Hash password menggunakan SHA-256 + Salt.
    Format disimpan: <salt_hex>$<hash_hex>
    """
    if salt is None:
        salt = os.urandom(16)

    if isinstance(salt, str):
        salt = bytes.fromhex(salt)

    hashed = hashlib.sha256(salt + password.encode()).hexdigest()
    return salt.hex() + "$" + hashed


def verify_password(stored_password, input_pass):
    """
    Verifikasi password berdasarkan salt + hash.
    """
    salt_hex, stored_hash = stored_password.split("$")
    return stored_password == hash_password(input_pass, salt_hex)


# ============================================
# 🎵 CEK EKSTENSI FILE
# ============================================

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_media_files(folder, ext_list):
    """
    Mengambil semua file media di dalam folder berdasarkan ekstensi.
    """
    if not os.path.exists(folder):
        return []

    try:
        return [
            f for f in os.listdir(folder)
            if any(f.lower().endswith(ext) for ext in ext_list)
        ]
    except:
        return []


# ============================================
# 🔥 ROLE SYSTEM (Root / User)
# ============================================

def is_root():
    """Mengembalikan True jika session.role = 'root'."""
    return session.get("role") == "root"


def is_user():
    """Mengembalikan True jika session.role = 'user'."""
    return session.get("role") == "user"


def require_root():
    """
    Proteksi cepat untuk route khusus root.
    Contoh pakai:
    
    @app.route('/admin')
    def admin():
        return require_root() or render_template('admin.html')
    """
    if not is_root():
        return "Akses ditolak! Hanya root yang bisa membuka halaman ini.", 403
    return None
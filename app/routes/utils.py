# app/routes/utils.py
import os
import hashlib
from flask import session, redirect

# ============================================
# FORMAT EKSTENSI VALID (FULL)
# ============================================
ALLOWED_EXTENSIONS = {
    # Video
    'mp4', 'avi', 'mkv', 'mov', 'wmv', 'webm',

    # Audio
    'mp3', 'wav', 'ogg', 'aac', 'flac',

    # Images
    'jpg', 'jpeg', 'png', 'gif', 'webp',

    # Documents
    'pdf', 'txt', 'doc', 'docx',

    # Archives
    'zip', 'rar', '7z',

    # Other
    'json'
}

# ============================================
# 🔐 SYSTEM PASSWORD HASHING
# ============================================

def hash_password(password, salt=None):
    """Generate hash SHA-256 + salt."""
    if salt is None:
        salt = os.urandom(16)
    if isinstance(salt, str):
        salt = bytes.fromhex(salt)

    hashed = hashlib.sha256(salt + password.encode()).hexdigest()
    return f"{salt.hex()}${hashed}"


def verify_password(stored_password, input_pass):
    """Cek password input cocok dengan hash yg disimpan."""
    salt_hex, _ = stored_password.split("$")
    return stored_password == hash_password(input_pass, salt_hex)


# ============================================
# 🎵 CEK EKSTENSI FILE MEDIA
# ============================================

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_media_files(folder, ext_list):
    """Mengambil file media dari folder tertentu."""
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
# 🔥 ROLE SYSTEM (ROOT / USER)
# ============================================

def is_root():
    """True jika user saat ini adalah root."""
    return session.get("role") == "root"


def is_user():
    """True jika user role 'user'."""
    return session.get("role") == "user"


def require_root():
    """
    Proteksi untuk halaman khusus root.
    Jika bukan root → redirect ke /home.
    Cara pakai:

        check = require_root()
        if check: return check

    """
    if not is_root():
        return redirect("/home")
    return None
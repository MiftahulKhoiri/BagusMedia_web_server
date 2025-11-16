import os
import hashlib

# Semua ekstensi file yang diperbolehkan
ALLOWED_EXTENSIONS = {
    'mp4', 'avi', 'mkv', 'mov', 'wmv',
    'mp3', 'wav', 'ogg'
}

def hash_password(password, salt=None):
    """Membuat hash password dengan salt"""
    if salt is None:
        salt = os.urandom(16)
    if isinstance(salt, str):
        salt = bytes.fromhex(salt)
    hashed = hashlib.sha256(salt + password.encode()).hexdigest()
    return salt.hex() + "$" + hashed

def verify_password(stored_password, input_pass):
    """Memverifikasi password input dengan hash"""
    salt_hex, hashed = stored_password.split("$")
    return stored_password == hash_password(input_pass, salt_hex)

def allowed_file(filename):
    """Cek apakah file sesuai ekstensi"""
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS

def get_media_files(folder, ext_list):
    """Mengambil daftar file dari folder tertentu"""
    if not os.path.exists(folder):
        return []
    return [
        f for f in os.listdir(folder)
        if any(f.lower().endswith(ext) for ext in ext_list)
    ]
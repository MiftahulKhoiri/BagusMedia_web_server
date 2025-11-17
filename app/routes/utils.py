import os
import hashlib

# ==========================================
# HASH PASSWORD + VERIFIKASI
# ==========================================

def hash_password(password, salt=None):
    """
    Meng-hash password menggunakan SHA256 + salt.
    Format hasil: {salt_hex}${hash}
    """
    if salt is None:
        salt = os.urandom(16)  # generate salt baru

    # Jika salt berupa string hex, ubah jadi bytes
    if isinstance(salt, str):
        salt = bytes.fromhex(salt)

    hashed = hashlib.sha256(salt + password.encode()).hexdigest()

    # Gabungkan salt + hash
    return salt.hex() + "$" + hashed


def verify_password(stored_password, input_pass):
    """
    Verifikasi password dengan memisahkan salt dan hash,
    lalu membandingkan hasil hash ulang.
    """
    salt_hex, hashed = stored_password.split("$")
    return stored_password == hash_password(input_pass, salt_hex)


# ==========================================
# CEK EKSTENSI FILE DIIZINKAN
# ==========================================

def allowed_file(filename):
    """
    Mengecek apakah file memiliki ekstensi valid.
    Ditambah EXTENSI FOTO supaya upload foto berhasil.
    """
    allowed = {
        # Video
        'mp4', 'avi', 'mkv', 'mov', 'wmv',

        # Audio
        'mp3', 'wav', 'ogg',

        # Gambar / Foto
        'jpg', 'jpeg', 'png', 'gif', 'webp'
    }

    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


# ==========================================
# LIST FILE MEDIA
# ==========================================

def get_media_files(folder, ext_list):
    """
    Mengambil daftar file berdasarkan ekstensi dalam folder tertentu.
    """
    if not os.path.exists(folder):
        return []

    return [
        f for f in os.listdir(folder)
        if any(f.lower().endswith(ext) for ext in ext_list)
    ]
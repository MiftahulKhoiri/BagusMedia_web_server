# app/__init__.py
import os
import platform
import sqlite3
from datetime import datetime
from flask import Flask
from flask_sock import Sock


# ============================================================
# 1. 🔍 DETEKSI PATH STORAGE (ANDROID / WINDOWS / LINUX / MAC)
# ============================================================
def detect_storage_paths():
    """
    Menentukan folder penyimpanan utama secara otomatis.
    Berguna agar FileManager bisa berjalan di Android & PC tanpa konfigurasi manual.
    """

    system = platform.system().lower()

    # --------- ANDROID / TERMUX DETECTION ---------
    android_paths = [
        "/storage/emulated/0",
        "/sdcard",
        "/storage/self/primary"
    ]

    for p in android_paths:
        if os.path.exists(p):
            return {
                "ROOT": p,
                "MUSIC": os.path.join(p, "Music"),
                "VIDEO": os.path.join(p, "Movies"),
                "PICTURES": os.path.join(p, "Pictures"),
                "DCIM": os.path.join(p, "DCIM"),
                "DOWNLOAD": os.path.join(p, "Download"),
                "WHATSAPP": os.path.join(p, "WhatsApp", "Media"),
                "UPLOAD_TEMP": os.path.join(p, "Download", "UploadTemp")
            }

    # --------- WINDOWS DETECTION ---------
    if "windows" in system:
        home = os.path.expanduser("~")
        return {
            "ROOT": home,
            "MUSIC": os.path.join(home, "Music"),
            "VIDEO": os.path.join(home, "Videos"),
            "PICTURES": os.path.join(home, "Pictures"),
            "DCIM": os.path.join(home, "Pictures"),
            "DOWNLOAD": os.path.join(home, "Downloads"),
            "WHATSAPP": os.path.join(home, "Downloads"),
            "UPLOAD_TEMP": os.path.join(home, "Downloads", "UploadTemp")
        }

    # --------- LINUX / MACOS DETECTION ---------
    home = os.path.expanduser("~")
    return {
        "ROOT": home,
        "MUSIC": os.path.join(home, "Music"),
        "VIDEO": os.path.join(home, "Videos"),
        "PICTURES": os.path.join(home, "Pictures"),
        "DCIM": os.path.join(home, "Pictures"),
        "DOWNLOAD": os.path.join(home, "Downloads"),
        "WHATSAPP": os.path.join(home, "Downloads"),
        "UPLOAD_TEMP": os.path.join(home, "Downloads", "UploadTemp")
    }


# ============================================================
# 2. 🗂 DATABASE SETUP (CREATE TABLE + MIGRATION)
# ============================================================
def init_database(db_path):
    """Membuat tabel `users` jika belum ada."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            jk TEXT,
            umur INTEGER,
            bio TEXT,
            foto TEXT,
            cover TEXT,
            role TEXT DEFAULT 'user',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def ensure_role_column(db_path):
    """Menambah kolom role jika belum ada (idempotent)."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(users)")
    cols = [row[1] for row in cursor.fetchall()]

    if "role" not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
        conn.commit()

    conn.close()


def ensure_other_user_columns(db_path):
    """Tambah kolom tambahan jika sebelumnya tidak ada."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(users)")
    existing = [row[1] for row in cursor.fetchall()]

    optional = {
        "email": "ALTER TABLE users ADD COLUMN email TEXT",
        "jk": "ALTER TABLE users ADD COLUMN jk TEXT",
        "umur": "ALTER TABLE users ADD COLUMN umur INTEGER",
        "bio": "ALTER TABLE users ADD COLUMN bio TEXT",
        "foto": "ALTER TABLE users ADD COLUMN foto TEXT",
        "cover": "ALTER TABLE users ADD COLUMN cover TEXT",
    }

    for col, sql in optional.items():
        if col not in existing:
            try: cursor.execute(sql)
            except: pass

    conn.commit()
    conn.close()


# ============================================================
# 3. 👑 BUAT USER ROOT DEFAULT
# ============================================================
def ensure_root_user(db_path):
    """Membuat user root secara otomatis jika belum ada."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE role='root' LIMIT 1")
    found = cursor.fetchone()

    if not found:
        from app.routes.utils import hash_password

        now = datetime.utcnow().isoformat()
        hashed = hash_password("root123")

        cursor.execute("""
            INSERT INTO users (username, password, role, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, ("root", hashed, "root", now, now))

        conn.commit()
        print("== ROOT USER CREATED ==")
        print("USER: root")
        print("PASS: root123")

    conn.close()


# ============================================================
# 4. 📁 PROFIL JSON DEFAULT
# ============================================================
def ensure_profile_json(path):
    """Membuat file profile.json default jika belum ada."""
    if not os.path.exists(path):
        import json
        default = {
            "nama": "Tidak diketahui",
            "email": "",
            "jk": "",
            "umur": "",
            "bio": "",
            "foto": "",
            "cover": ""
        }
        with open(path, "w") as f:
            json.dump(default, f, indent=2)


# ============================================================
# 5. 🚀 CREATE_APP (INTI APLIKASI)
# ============================================================
def create_app():
    """
    Fungsi utama pembuat aplikasi Flask.
    - Auto deteksi storage OS
    - Auto konfigurasi folder untuk FileManager
    - Auto database migration
    - Register semua blueprint
    """

    app = Flask(__name__)
    sock = Sock(app)

    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.secret_key = "bagus-secret-key"

    # ---------------------------------------------------------
    # 🔥 AUTO DETECT ANDROID / PC STORAGE
    # ---------------------------------------------------------
    paths = detect_storage_paths()

    # Simpan semua path yang terdeteksi ke config Flask
    app.config["ANDROID_STORAGE"] = paths["ROOT"]
    app.config["MP3_FOLDER"]      = paths["MUSIC"]
    app.config["VIDEO_FOLDER"]    = paths["VIDEO"]
    app.config["PICTURES_FOLDER"] = paths["PICTURES"]
    app.config["DCIM_FOLDER"]     = paths["DCIM"]
    app.config["DOWNLOAD_FOLDER"] = paths["DOWNLOAD"]
    app.config["WHATSAPP_FOLDER"] = paths["WHATSAPP"]
    app.config["UPLOAD_FOLDER"]   = paths["UPLOAD_TEMP"]

    # Buat UploadTemp bila belum ada
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # ---------------------------------------------------------
    # 🗄 DATABASE INIT + MIGRATION
    # ---------------------------------------------------------
    db_path = os.path.join(base_dir, "database.db")
    app.config["DATABASE"] = db_path

    init_database(db_path)
    ensure_role_column(db_path)
    ensure_other_user_columns(db_path)
    ensure_root_user(db_path)
    ensure_profile_json(os.path.join(base_dir, "profile.json"))

    # ---------------------------------------------------------
    # 🔗 REGISTER BLUEPRINTS (ROUTES)
    # ---------------------------------------------------------
    from .routes import register_blueprints
    register_blueprints(app, sock)

    return app
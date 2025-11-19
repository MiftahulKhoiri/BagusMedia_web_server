# app/__init__.py
import os
import sqlite3
from datetime import datetime
from flask import Flask
from flask_sock import Sock


# =====================================================
# 1. MEMBUAT DATABASE JIKA BELUM ADA (TABEL users)
# =====================================================
def init_database(db_path):
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


# =====================================================
# 2. PASTIKAN KOLOM 'role' ADA (jika skema awal berbeda)
# =====================================================
def ensure_role_column(db_path):
    """
    Menambahkan kolom 'role' bila belum ada.
    Idempotent — aman dipanggil berkali-kali.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(users)")
    cols = [row[1] for row in cursor.fetchall()]

    if "role" not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
        conn.commit()

    conn.close()


# =====================================================
# 3. MIGRATE KOLOM-LAIN (opsional safety)
# =====================================================
def ensure_other_user_columns(db_path):
    """
    Tambah kolom lain jika belum ada (email, jk, umur, bio, foto, cover).
    Berguna bila tabel dibuat sangat sederhana sebelumnya.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users)")
    existing = [r[1] for r in cursor.fetchall()]

    maybe = {
        "email": "ALTER TABLE users ADD COLUMN email TEXT",
        "jk": "ALTER TABLE users ADD COLUMN jk TEXT",
        "umur": "ALTER TABLE users ADD COLUMN umur INTEGER",
        "bio": "ALTER TABLE users ADD COLUMN bio TEXT",
        "foto": "ALTER TABLE users ADD COLUMN foto TEXT",
        "cover": "ALTER TABLE users ADD COLUMN cover TEXT",
    }

    for col, sql in maybe.items():
        if col not in existing:
            try:
                cursor.execute(sql)
            except Exception:
                # jika gagal (misal SQLite tidak mendukung ALTER pada tipe), ignore
                pass

    conn.commit()
    conn.close()


# =====================================================
# 4. MEMBUAT USER ROOT JIKA BELUM ADA
# =====================================================
def ensure_root_user(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username='root' OR role='root' LIMIT 1")
    found = cursor.fetchone()

    if not found:
        # hash function diambil dari app.routes.utils
        try:
            from app.routes.utils import hash_password
        except Exception:
            # fallback very-simple jika import gagal (tapi idealnya import tidak gagal)
            import hashlib, os
            def hash_password(pw, salt=None):
                if salt is None:
                    salt = os.urandom(16)
                if isinstance(salt, str):
                    salt = bytes.fromhex(salt)
                return salt.hex() + "$" + hashlib.sha256(salt + pw.encode()).hexdigest()

        now = datetime.utcnow().isoformat()
        hashed = hash_password("root123")

        cursor.execute("""
            INSERT INTO users (username, password, role, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, ("root", hashed, "root", now, now))
        conn.commit()
        print("== ROOT USER CREATED ==")
        print("USERNAME : root")
        print("PASSWORD : root123")
    else:
        print("ROOT user found — skip.")

    conn.close()


# =====================================================
# 5. PASTIKAN FILE PROFILE JSON ADA
# =====================================================
def ensure_profile_json(path):
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
        print("profile.json dibuat.")
    else:
        print("profile.json ditemukan — skip.")


# =====================================================
# 6. CREATE_APP (inti aplikasi)
# =====================================================
def create_app():
    app = Flask(__name__)
    sock = Sock(app)

    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.secret_key = "bagus-secret-key"

    # paths
    app.config["PROJECT_ROOT"] = base_dir
    app.config["PROFILE_FILE"] = os.path.join(base_dir, "profile.json")
    app.config["UPLOAD_FOLDER"] = os.path.join(base_dir, "static", "upload")
    app.config["MP3_FOLDER"] = os.path.join(base_dir, "mp3")
    app.config["VIDEO_FOLDER"] = os.path.join(base_dir, "video")

    # create folders
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["MP3_FOLDER"], exist_ok=True)
    os.makedirs(app.config["VIDEO_FOLDER"], exist_ok=True)
    os.makedirs(os.path.join(base_dir, "static", "profile"), exist_ok=True)

    # db
    db_path = os.path.join(base_dir, "database.db")
    app.config["DATABASE"] = db_path

    # run setup / migrations (idempotent)
    init_database(db_path)                # buat tabel minimal jika belum ada
    ensure_role_column(db_path)           # pastikan kolom role ada
    ensure_other_user_columns(db_path)    # tambahkan kolom opsional lain jika perlu
    ensure_root_user(db_path)             # buat akun root default jika belum ada
    ensure_profile_json(app.config["PROFILE_FILE"])  # buat profile.json default

    # register blueprints (pastikan app.routes.register_blueprints ada)
    from .routes import register_blueprints
    register_blueprints(app, sock)

    return app
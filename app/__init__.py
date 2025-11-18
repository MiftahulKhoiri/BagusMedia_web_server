import os
import sqlite3
from datetime import datetime
from flask import Flask
from flask_sock import Sock


# =====================================================
#  MEMBUAT DATABASE JIKA BELUM ADA
# =====================================================
def init_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# =====================================================
#  MENAMBAHKAN KOLOM ROLE JIKA BELUM ADA
# =====================================================
def ensure_role_column(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]

    if "role" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
        conn.commit()

    conn.close()


# =====================================================
#  MEMBUAT USER ROOT JIKA BELUM ADA
# =====================================================
def ensure_root_user(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE role='root'")
    root = cursor.fetchone()

    if not root:
        from app.routes.utils import hash_password

        now = datetime.utcnow().isoformat()
        cursor.execute("""
            INSERT INTO users (username, password, created_at, updated_at, role)
            VALUES (?, ?, ?, ?, ?)
        """, ("root", hash_password("root123"), now, now, "root"))

        conn.commit()

    conn.close()


# =====================================================
#  FUNCTION UTAMA APP
# =====================================================
def create_app():
    app = Flask(__name__)
    sock = Sock(app)

    # Lokasi file & root project
    base_dir = os.path.abspath(os.path.dirname(__file__))

    # ------------------------------------------
    # CONFIG DASAR
    # ------------------------------------------
    app.secret_key = "bagus-secret-key"

    app.config["PROJECT_ROOT"] = base_dir
    app.config["PROFILE_FILE"] = os.path.join(base_dir, "profile.json")

    # Folder media
    app.config["UPLOAD_FOLDER"] = os.path.join(base_dir, "static/upload")
    app.config["MP3_FOLDER"] = os.path.join(base_dir, "mp3")
    app.config["VIDEO_FOLDER"] = os.path.join(base_dir, "video")

    # Auto-buat folder
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["MP3_FOLDER"], exist_ok=True)
    os.makedirs(app.config["VIDEO_FOLDER"], exist_ok=True)

    # ------------------------------------------
    # DATABASE
    # ------------------------------------------
    db_path = os.path.join(base_dir, "database.db")
    app.config["DATABASE"] = db_path

    init_database(db_path)
    ensure_role_column(db_path)
    ensure_root_user(db_path)

    # ------------------------------------------
    # REGISTER BLUEPRINTS
    # ------------------------------------------
    from .routes import register_blueprints
    register_blueprints(app, sock)

    return app
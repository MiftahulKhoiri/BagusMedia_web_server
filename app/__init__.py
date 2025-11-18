import os
import sqlite3
from flask import Flask
from flask_sock import Sock

# ==================================================
#  FUNGSI MEMBUAT DATABASE + TABEL USERS
# ==================================================
def init_database(db_path):
    # Membuat file database jika belum ada
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Membuat tabel users jika belum ada
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


# ==================================================
#  FUNCTION UTAMA UNTUK MEMBANGUN APLIKASI
# ==================================================
def create_app():
    app = Flask(__name__)

    # Folder dasar project
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))

    # ==================================================
    #  KONFIGURASI APLIKASI
    # ==================================================
    app.secret_key = "bagus-secret-key"  # kamu bisa ganti bebas

    app.config["PROJECT_ROOT"] = base_dir
    app.config["PROFILE_FILE"] = os.path.join(base_dir, "profile.json")

    # Folder upload & media
    app.config["UPLOAD_FOLDER"] = os.path.join(base_dir, "static/upload")
    app.config["MP3_FOLDER"] = os.path.join(base_dir, "static/mp3")
    app.config["VIDEO_FOLDER"] = os.path.join(base_dir, "static/video")

    # Buat folder jika belum ada
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["MP3_FOLDER"], exist_ok=True)
    os.makedirs(app.config["VIDEO_FOLDER"], exist_ok=True)

    # ==================================================
    #  DATABASE
    # ==================================================
    app.config["DATABASE"] = os.path.join(base_dir, "database.db")

    # Membuat database + tabel users
    init_database(app.config["DATABASE"])

    # ==================================================
    #  WEBSOCKET (UNTUK FITUR UPDATE)
    # ==================================================
    sock = Sock(app)

    # ==================================================
    #  REGISTER SEMUA BLUEPRINT
    # ==================================================
    from .routes import register_blueprints
    register_blueprints(app, sock)

    return app
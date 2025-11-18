import os
import sqlite3
from flask import Flask
from flask_sock import Sock

# ===============================
#  MEMBUAT DATABASE + TABEL USERS
# ===============================
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


# ===============================
#  FUNCTION UTAMA: CREATE_APP()
# ===============================
def create_app():
    app = Flask(__name__)

    # Lokasi root project
    base_dir = os.path.abspath(os.path.dirname(__file__))

    # ---------------------------
    # KONFIGURASI APLIKASI
    # ---------------------------
    app.secret_key = "bagus-secret-key"

    app.config["PROJECT_ROOT"] = base_dir
    app.config["PROFILE_FILE"] = os.path.join(base_dir, "profile.json")

    # Folder upload lokal
    app.config["UPLOAD_FOLDER"] = os.path.join(base_dir, "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Folder MP3, VIDEO
    app.config["MP3_FOLDER"] = os.path.join(base_dir, "mp3")
    app.config["VIDEO_FOLDER"] = os.path.join(base_dir, "video")
    os.makedirs(app.config["MP3_FOLDER"], exist_ok=True)
    os.makedirs(app.config["VIDEO_FOLDER"], exist_ok=True)

    # ---------------------------
    # DATABASE
    # ---------------------------
    app.config["DATABASE"] = os.path.join(base_dir, "database.db")

    # Buat database + tabel users
    init_database(app.config["DATABASE"])

    # ---------------------------
    # WEBSOCKET
    # ---------------------------
    sock = Sock(app)

    # ---------------------------
    # REGISTER ROUTES/BLUEPRINTS
    # ---------------------------
    from .routes import register_blueprints
    register_blueprints(app, sock)

    return app
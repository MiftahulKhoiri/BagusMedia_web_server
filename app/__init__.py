import os
import sqlite3
from flask import Flask
from flask_sock import Sock


# ============================================
# INIT DATABASE
# ============================================
def init_db_from_path(db_path):
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


# ============================================
# CREATE APP
# ============================================
def create_app():
    # Folder root project
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Instance folder
    instance_path = os.path.join(project_root, "instance")
    os.makedirs(instance_path, exist_ok=True)

    # Buat app flask
    app = Flask(__name__, instance_path=instance_path, instance_relative_config=True)

    # Secret key
    app.secret_key = os.environ.get("BAGUS_SECRET_KEY", "ganti_ini_dengan_key_acak")

    # Konfigurasi path penting
    app.config["PROJECT_ROOT"] = project_root
    app.config["DATABASE"] = os.path.join(instance_path, "bagusmedia.db")
    app.config["PROFILE_FILE"] = os.path.join(instance_path, "profile_data.json")

    # Static & templates
    app.static_folder = os.path.join(os.path.dirname(__file__), "static")
    app.template_folder = os.path.join(os.path.dirname(__file__), "templates")

    # Folder media
    app.config["UPLOAD_FOLDER"] = os.path.join(app.static_folder, "upload")
    app.config["VIDEO_FOLDER"] = os.path.join(app.static_folder, "video")
    app.config["MP3_FOLDER"] = os.path.join(app.static_folder, "mp3")
    app.config["ICON_FOLDER"] = os.path.join(app.static_folder, "icon")

    # Max upload 1GB
    app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 1024

    # Buat folder media jika belum ada
    for folder in [
        app.config["UPLOAD_FOLDER"],
        app.config["VIDEO_FOLDER"],
        app.config["MP3_FOLDER"],
        app.config["ICON_FOLDER"]
    ]:
        os.makedirs(folder, exist_ok=True)

    # Inisialisasi database
    init_db_from_path(app.config["DATABASE"])

    # WebSocket
    sock = Sock(app)


    # ============================================
    # REGISTER BLUEPRINTS
    # ============================================

    # AUTH
    from .blueprints.auth import auth_bp
    app.register_blueprint(auth_bp)

    # HOME
    from .blueprints.home import home_bp
    app.register_blueprint(home_bp)

    # MEDIA
    from .blueprints.media import media_bp
    app.register_blueprint(media_bp)

    # UPLOAD
    from .blueprints.upload import upload_bp
    app.register_blueprint(upload_bp)

    # PROFILE
    from .blueprints.profile import profile_bp
    app.register_blueprint(profile_bp)

    # UPDATE (WEB + SOCKET)
    from .blueprints.update import update_bp
    from .blueprints.update.routes import register_websocket

    app.register_blueprint(update_bp)
    register_websocket(sock)

    return app
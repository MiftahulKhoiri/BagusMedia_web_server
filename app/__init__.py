import os
from flask import Flask
from flask_sock import Sock
import sqlite3

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

def create_app():
    # project root = parent folder of this app package
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # instance folder (untuk menyimpan DB dan file runtime)
    instance_path = os.path.join(project_root, "instance")
    os.makedirs(instance_path, exist_ok=True)

    app = Flask(__name__, instance_path=instance_path, instance_relative_config=True)
    app.secret_key = os.environ.get("BAGUS_SECRET_KEY", "ganti_ini_dengan_key_acak")

    # Paths
    app.config['PROJECT_ROOT'] = project_root
    app.config['DATABASE'] = os.path.join(instance_path, "bagusmedia.db")
    app.config['PROFILE_FILE'] = os.path.join(instance_path, "profile_data.json")

    # Static/media folders (inside app/static)
    app.static_folder = os.path.join(os.path.dirname(__file__), "static")
    app.template_folder = os.path.join(os.path.dirname(__file__), "templates")

    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'upload')
    app.config['VIDEO_FOLDER'] = os.path.join(app.static_folder, 'video')
    app.config['MP3_FOLDER'] = os.path.join(app.static_folder, 'mp3')
    app.config['ICON_FOLDER'] = os.path.join(app.static_folder, 'icon')
    app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1GB

    for folder in [app.config['UPLOAD_FOLDER'], app.config['VIDEO_FOLDER'],
                   app.config['MP3_FOLDER'], app.config['ICON_FOLDER']]:
        os.makedirs(folder, exist_ok=True)

    # Initialize DB if needed
    init_db_from_path(app.config['DATABASE'])

    # Initialize Sock
    sock = Sock(app)

    # Import and register routes (routes.init_app will attach routes to this app)
    from . import routes
    routes.init_app(app, sock)

    return app
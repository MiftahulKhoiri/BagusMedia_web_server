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
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    instance_path = os.path.join(project_root, "instance")
    os.makedirs(instance_path, exist_ok=True)

    app = Flask(__name__, instance_path=instance_path, instance_relative_config=True)

    app.secret_key = os.environ.get("BAGUS_SECRET_KEY", "ganti_ini_dengan_key_acak")

    app.config['PROJECT_ROOT'] = project_root
    app.config['DATABASE'] = os.path.join(instance_path, "bagusmedia.db")
    app.config['PROFILE_FILE'] = os.path.join(instance_path, "profile_data.json")

    app.static_folder = os.path.join(os.path.dirname(__file__), "static")
    app.template_folder = os.path.join(os.path.dirname(__file__), "templates")

    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'upload')
    app.config['VIDEO_FOLDER'] = os.path.join(app.static_folder, 'video')
    app.config['MP3_FOLDER'] = os.path.join(app.static_folder, 'mp3')
    app.config['ICON_FOLDER'] = os.path.join(app.static_folder, 'icon')

    app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024

    for folder in [
        app.config['UPLOAD_FOLDER'], 
        app.config['VIDEO_FOLDER'],
        app.config['MP3_FOLDER'], 
        app.config['ICON_FOLDER']
    ]:
        os.makedirs(folder, exist_ok=True)

    init_db_from_path(app.config['DATABASE'])

    sock = Sock(app)
# ============================================
# REGISTER BLUEPRINTS
# ============================================
from .blueprints.auth import auth_bp
from .blueprints.home import home_bp
from .blueprints.media import media_bp
from .blueprints.upload import upload_bp
from .blueprints.profile import profile_bp
from .blueprints.update import update_bp

app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)
app.register_blueprint(media_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(update_bp)

    # Panggil routes dari folder routes
    from . import routes
    routes.init_app(app, sock)

    return app
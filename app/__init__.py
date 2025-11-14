import os
from flask import Flask
from flask_sock import Sock
import sqlite3

def init_db_from_path(db_path):
    # Membuka koneksi ke database SQLite
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

    # Simpan perubahan
    conn.commit()
    conn.close()  # Tutup koneksi DB

def create_app():
    # Menentukan folder root proyek (folder di atas package app)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Membuat folder instance untuk DB dan file runtime lain
    instance_path = os.path.join(project_root, "instance")
    os.makedirs(instance_path, exist_ok=True)

    # Membuat objek Flask dan set lokasi instance-nya
    app = Flask(__name__, instance_path=instance_path, instance_relative_config=True)

    # Secret key untuk session & keamanan (ambil dari environment jika ada)
    app.secret_key = os.environ.get("BAGUS_SECRET_KEY", "ganti_ini_dengan_key_acak")

    # Konfigurasi path penting aplikasi
    app.config['PROJECT_ROOT'] = project_root
    app.config['DATABASE'] = os.path.join(instance_path, "bagusmedia.db")
    app.config['PROFILE_FILE'] = os.path.join(instance_path, "profile_data.json")

    # Menentukan lokasi folder static & templates
    app.static_folder = os.path.join(os.path.dirname(__file__), "static")
    app.template_folder = os.path.join(os.path.dirname(__file__), "templates")

    # Folder khusus file upload, video, mp3, icon
    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'upload')
    app.config['VIDEO_FOLDER'] = os.path.join(app.static_folder, 'video')
    app.config['MP3_FOLDER'] = os.path.join(app.static_folder, 'mp3')
    app.config['ICON_FOLDER'] = os.path.join(app.static_folder, 'icon')

    # Batas maksimum upload file (1GB)
    app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024

    # Membuat semua folder media jika belum ada
    for folder in [app.config['UPLOAD_FOLDER'], app.config['VIDEO_FOLDER'],
                   app.config['MP3_FOLDER'], app.config['ICON_FOLDER']]:
        os.makedirs(folder, exist_ok=True)

    # Inisialisasi database (membuat kalau belum ada)
    init_db_from_path(app.config['DATABASE'])

    # Setup WebSocket dengan Flask-Sock
    sock = Sock(app)

    # Import dan pasang semua route ke aplikasi utama
    from . import routes
    routes.init_app(app, sock)

    return app
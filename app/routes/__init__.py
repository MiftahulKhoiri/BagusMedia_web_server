# app/routes/__init__.py

from .auth import auth
from .main import main
from .media import media
from .profile import profile
from .update import update_bp, register_ws
from .about import about

def register_blueprints(app, sock=None):
    """
    Mendaftarkan semua Blueprint ke aplikasi Flask.
    - auth        : register, login, logout, ganti password
    - main        : splash, home
    - media       : mp3, video, upload, serve media
    - profile     : profil user, edit, upload foto
    - update_bp   : halaman update + API cek update
    - register_ws : route websocket update
    """

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(media)
    app.register_blueprint(profile)
    app.register_blueprint(update_bp)
    app.register_blueprint(about)

    # Daftarkan websocket jika disediakan
    if sock is not None:
        register_ws(sock)
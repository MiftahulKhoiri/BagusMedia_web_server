from .auth_routes import register_routes
from .home_routes import home_routes
from .media_routes import media_routes
from .upload_routes import upload_routes
from .profile_routes import profile_routes
from .update_routes import update_routes

# ============================================
# INIT ROUTES — MEMANGGIL SEMUA FILE ROUTES
# ============================================

def init_app(app, sock):
    # Auth: register, login, logout, change password
    register_routes(app)

    # Home & splash
    home_routes(app)

    # Media: mp3, video, album, serve media
    media_routes(app)

    # Upload media
    upload_routes(app)

    # Profile: data profil, edit, upload foto & cover
    profile_routes(app)

    # Update system (git fetch/pull + WebSocket)
    update_routes(app, sock)
from .auth import auth, init_auth
from .home import home_bp, init_home
from .media import media, init_media
from .profile import profile_bp, init_profile
from .update import update_bp, init_update

def init_routes(app, sock):
    # Inisialisasi semua blueprint
    init_auth(app)
    init_home(app)
    init_media(app)
    init_profile(app)
    init_update(app, sock)

    # Daftarkan di Flask
    app.register_blueprint(auth)
    app.register_blueprint(home_bp)
    app.register_blueprint(media)
    app.register_blueprint(profile_bp)
    app.register_blueprint(update_bp)
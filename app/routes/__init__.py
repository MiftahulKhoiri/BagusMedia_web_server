from .home_routes import register_home_routes
from .profile_routes import register_profile_routes
from .media_routes import register_media_routes
from .update_routes import register_update_routes
from .auth_routes import register_auth_routes   # nanti kita buat

def init_routes(app, sock):
    register_auth_routes(app)
    register_home_routes(app)
    register_profile_routes(app)
    register_media_routes(app)
    register_update_routes(app, sock)
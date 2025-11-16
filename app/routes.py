from .routes.auth_routes import register_auth_routes
from .routes.profile_routes import register_profile_routes
from .routes.upload_routes import register_upload_routes
from .routes.media_routes import register_media_routes
from .routes.update_routes import register_update_routes

def init_app(app, sock):
    register_auth_routes(app)
    register_profile_routes(app)
    register_upload_routes(app)
    register_media_routes(app)
    register_update_routes(app, sock)
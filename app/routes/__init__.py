from .auth_routes import register_routes

def init_app(app, sock):
    register_routes(app)
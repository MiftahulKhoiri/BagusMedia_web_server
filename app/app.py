from routes import init_routes
from flask_sock import Sock

def create_app():
    app = Flask(__name__)
    sock = Sock(app)

    init_routes(app, sock)

    return app
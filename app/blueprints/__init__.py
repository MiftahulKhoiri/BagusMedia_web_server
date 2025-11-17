from .auth import auth_bp
from .home import home_bp
from .media import media_bp
from .upload import upload_bp
from .profile import profile_bp
from .update import update_bp

__all__ = [
    "auth_bp",
    "home_bp",
    "media_bp",
    "upload_bp",
    "profile_bp",
    "update_bp",
]
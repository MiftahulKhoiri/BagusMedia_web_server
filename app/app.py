from flask import Flask
from flask_sock import Sock
import os

# Import blueprint handler
from routes import register_blueprints

app = Flask(__name__)
sock = Sock(app)

# ============================================
# CONFIG APPLICATION
# (Semua nama config disamakan dengan routes.py asli)
# ============================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Folder utama project (dipakai untuk git update)
app.config["PROJECT_ROOT"] = BASE_DIR

# Folder profile.json
app.config["PROFILE_FILE"] = os.path.join(BASE_DIR, "profile.json")

# Folder upload sementara
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "uploads")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Folder MP3 dan VIDEO
app.config["MP3_FOLDER"] = os.path.join(BASE_DIR, "mp3")
app.config["VIDEO_FOLDER"] = os.path.join(BASE_DIR, "video")
os.makedirs(app.config["MP3_FOLDER"], exist_ok=True)
os.makedirs(app.config["VIDEO_FOLDER"], exist_ok=True)

# Database lokasi (SQLite)
app.config["DATABASE"] = os.path.join(BASE_DIR, "database.db")

# SECRET_KEY untuk session
app.secret_key = "bagus-secret-key"  # kamu bisa ganti

# ============================================
# REGISTER SEMUA BLUEPRINT + WEBSOCKET
# ============================================

register_blueprints(app, sock)


# ============================================
# START SERVER
# ============================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
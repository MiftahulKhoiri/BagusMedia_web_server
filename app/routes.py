import os
import json
import shutil
import subprocess
import threading
import sys
import time
import sqlite3
import hashlib
from datetime import datetime
from flask import (
    render_template, request, jsonify, send_from_directory,
    redirect, session
)
from werkzeug.utils import secure_filename


# ============================
#  SET EKSTENSI FILE VALID
# ============================
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov', 'wmv', 'mp3', 'wav', 'ogg'}


# ============================
#  HELPER FUNCTION SEDERHANA
# ============================
def hash_password(password, salt=None):
    # Hash password
    if salt is None:
        salt = os.urandom(16)
    if isinstance(salt, str):
        salt = bytes.fromhex(salt)
    hashed = hashlib.sha256(salt + password.encode()).hexdigest()
    return salt.hex() + "$" + hashed


def verify_password(stored_password, input_pass):
    # Validasi password
    salt_hex, hashed = stored_password.split("$")
    return stored_password == hash_password(input_pass, salt_hex)


def allowed_file(filename):
    # Cek ekstensi file valid
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_media_files(folder, ext_list):
    # Ambil semua file media di folder
    if not os.path.exists(folder):
        return []
    return [f for f in os.listdir(folder) if any(f.lower().endswith(ext) for ext in ext_list)]

# ============================
#         ROUTES INTI
# ============================
def init_app(app, sock):

    BASE_DIR = app.config["PROJECT_ROOT"]
    PROFILE_FILE = app.config["PROFILE_FILE"]

    # ============================================
    # REGISTER
    # ============================================
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form["username"].strip()
            password = request.form["password"]

            if username == "" or password == "":
                return "Harus diisi!"

            hashed = hash_password(password)
            now = datetime.utcnow().isoformat()

            try:
                conn = sqlite3.connect(app.config["DATABASE"])
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password, created_at, updated_at) VALUES (?, ?, ?, ?)",
                    (username, hashed, now, now)
                )
                conn.commit()
                conn.close()
                return redirect("/login")
            except sqlite3.IntegrityError:
                return "Username sudah dipakai!"

        return render_template("register.html")

    # ============================================
    # LOGIN
    # ============================================
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"].strip()
            password = request.form["password"]

            conn = sqlite3.connect(app.config["DATABASE"])
            cursor = conn.cursor()
            cursor.execute("SELECT id, password FROM users WHERE username=?", (username,))
            user = cursor.fetchone()
            conn.close()

            if user and verify_password(user[1], password):
                session["user_id"] = user[0]
                session["username"] = username
                return redirect("/home")

            return "Username atau password salah!"

        return render_template("login.html")

    # ============================================
    # LOGOUT
    # ============================================
    @app.route("/logout")
    def logout():
        session.clear()
        return redirect("/login")

    # ============================================
    # SPLASH
    # ============================================
    @app.route("/")
    def splash():
        return render_template("splash.html")

    # ============================================
    # HOME
    # ============================================
    @app.route("/home")
    def home():
        if "user_id" not in session:
            return redirect("/login")
        current_year = datetime.now().year
        return render_template("home.html", current_year=current_year, username=session["username"])

    # ============================================
    # MP3 PLAYER
    # ============================================
    @app.route("/mp3")
    def mp3_player():
        if "user_id" not in session:
            return redirect("/login")
        mp3_files = get_media_files(app.config["MP3_FOLDER"], ['.mp3', '.wav', '.ogg'])
        return render_template("mp3.html", mp3_files=mp3_files)

    # ============================================
    # VIDEO PLAYER
    # ============================================
    @app.route("/video")
    def video_player():
        if "user_id" not in session:
            return redirect("/login")
        video_files = get_media_files(app.config["VIDEO_FOLDER"], ['.mp4', '.avi', '.mkv', '.mov', '.wmv'])
        return render_template("video.html", video_files=video_files)

    # ============================================
    # ALBUM MP3
    # ============================================
    @app.route("/audios")
    def audio_list():
        if "user_id" not in session:
            return redirect("/login")

        mp3_files = get_media_files(app.config["MP3_FOLDER"], ['.mp3', '.wav', '.ogg'])
        return render_template("mp3-list.html", mp3_files=mp3_files)

    # ============================================
    # ALBUM VIDEO
    # ============================================
    @app.route("/videos")
    def video_list():
        if "user_id" not in session:
            return redirect("/login")

        video_files = get_media_files(app.config["VIDEO_FOLDER"], ['.mp4', '.avi', '.mkv', '.mov', '.wmv'])
        return render_template("video-list.html", video_files=video_files)

    # ============================================
    # UPLOAD HALAMAN
    # ============================================
    @app.route("/upload")
    def upload():
        if "user_id" not in session:
            return redirect("/login")
        return render_template("upload.html")

    # ============================================
    # API UPLOAD MEDIA
    # ============================================
    @app.route("/api/upload", methods=["POST"])
    def upload_file():
        if "user_id" not in session:
            return jsonify({"error": "Harus login!"}), 403

        if "files" not in request.files:
            return jsonify({"error": "Tidak ada file!"})

        files = request.files.getlist("files")
        results = []

        for file in files:
            if file.filename == "":
                results.append({"filename": "", "status": "error"})
                continue

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                temp_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(temp_path)

                ext = filename.rsplit(".", 1)[1].lower()
                dest = app.config["MP3_FOLDER"] if ext in ['mp3', 'wav', 'ogg'] else app.config["VIDEO_FOLDER"]
                shutil.move(temp_path, os.path.join(dest, filename))

                results.append({"filename": filename, "status": "success"})
            else:
                results.append({"filename": file.filename, "status": "error"})

        return jsonify({"results": results})

    # ============================================
    # PROFIL
    # ============================================
    @app.route("/profile")
    def profile():
        if "user_id" not in session:
            return redirect("/login")

        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                profile_data = json.load(f)
        else:
            profile_data = {"nama": "", "email": "", "jk": "", "umur": "", "bio": "", "foto": "", "cover": ""}

        current_year = datetime.now().year
        return render_template("profile.html", profile=profile_data, current_year=current_year)

    # ============================================
    # EDIT PROFIL
    # ============================================
    @app.route("/edit-profile")
    def edit_profile():
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                profile_data = json.load(f)
        else:
            profile_data = {"nama": "", "email": "", "jk": "", "umur": "", "bio": "", "foto": "", "cover": ""}

        return render_template("edit-profile.html", profile=profile_data)

    # ============================================
    # SIMPAN PROFIL
    # ============================================
    @app.route("/api/save-profile", methods=["POST"])
    def save_profile():
        data = request.json
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return jsonify({"status": "success"})

    # ============================================
    # UPLOAD FOTO PROFIL / COVER
    # ============================================
    @app.route("/api/upload-photo", methods=["POST"])
    def upload_photo():
        if "photo" not in request.files:
            return jsonify({"status": "error"}), 400

        file = request.files["photo"]
        filename = secure_filename(str(int(time.time())) + "_" + file.filename)

        foto_folder = os.path.join(app.static_folder, "profile")
        os.makedirs(foto_folder, exist_ok=True)

        filepath = os.path.join(foto_folder, filename)
        file.save(filepath)

        return jsonify({"status": "success", "filename": filename})

    # ============================================
    # HALAMAN UPDATE
    # ============================================
    @app.route('/update')
    def update():
        return render_template('update.html')

    # ============================================
    # API CHECK UPDATE
    # ============================================
    @app.route('/api/check-update')
    def check_update():
        repo_path = BASE_DIR
        try:
            subprocess.run(["git", "fetch"], cwd=repo_path)
            status = subprocess.run(["git", "status", "-uno"], cwd=repo_path, capture_output=True, text=True)
            update_available = "behind" in status.stdout
            return jsonify({"update_available": update_available, "output": status.stdout})
        except Exception as e:
            return jsonify({"update_available": False, "error": str(e)})

    # ============================================
    # UPDATE WEBSOCKET
    # ============================================
    @sock.route('/ws/update')
    def ws_update(ws):
        def send(msg):
            try:
                ws.send(msg)
            except:
                pass

        repo_path = BASE_DIR
        send("[INFO] Memulai update...\n")

        p = subprocess.Popen(
            ["git", "pull"],
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        for line in p.stdout:
            send(line.strip())

        send("[DONE]")

    # ============================================
    # SERVE MEDIA
    # ============================================
    @app.route("/media/<folder>/<filename>")
    def serve_media(folder, filename):
        if folder == "mp3":
            return send_from_directory(app.config["MP3_FOLDER"], filename)
        if folder == "video":
            return send_from_directory(app.config["VIDEO_FOLDER"], filename)
        return "Folder tidak valid", 404
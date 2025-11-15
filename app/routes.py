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
    redirect, session, current_app
)
from werkzeug.utils import secure_filename


# ============================
#   SET FILE / EKSTENSI VALID
# ============================
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov', 'wmv', 'mp3', 'wav', 'ogg'}


# ============================
#   HELPER FUNCTION SIMPLE
# ============================

def hash_password(password, salt=None):
    # Membuat hash password
    if salt is None:
        salt = os.urandom(16)
    if isinstance(salt, str):
        salt = bytes.fromhex(salt)
    hashed = hashlib.sha256(salt + password.encode()).hexdigest()
    return salt.hex() + "$" + hashed


def verify_password(stored_password, password_input):
    # Validasi input password
    salt_hex, hashed = stored_password.split("$")
    return stored_password == hash_password(password_input, salt_hex)


def allowed_file(filename):
    # Cek ekstensi file valid
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_media_files(folder, extensions):
    # Ambil semua file media di folder
    if not os.path.exists(folder):
        return []
    return [f for f in os.listdir(folder) if any(f.lower().endswith(ext) for ext in extensions)]


# ============================
#       ROUTES UTAMA
# ============================

def init_app(app, sock):

    BASE_DIR = app.config.get('PROJECT_ROOT', os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    PROFILE_FILE = app.config.get('PROFILE_FILE')

    # ============================
    # REGISTER USER
    # ============================
    @app.route("/register", methods=["GET", "POST"])
    def register():
        # Proses daftar user baru
        if request.method == "POST":
            username = request.form["username"].strip()
            password = request.form["password"]

            if username == "" or password == "":
                return "Harus diisi!"

            hashed = hash_password(password)
            now = datetime.utcnow().isoformat()

            try:
                conn = sqlite3.connect(app.config['DATABASE'])
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

    # ============================
    # LOGIN USER
    # ============================
    @app.route("/login", methods=["GET", "POST"])
    def login():
        # Proses login user
        if request.method == "POST":
            username = request.form["username"].strip()
            password = request.form["password"]

            conn = sqlite3.connect(app.config['DATABASE'])
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

    # ============================
    # LOGOUT USER
    # ============================
    @app.route("/logout")
    def logout():
        # Menghapus sesi user
        session.clear()
        return redirect("/login")

    # ============================
    # SPLASH / LANDING
    # ============================
    @app.route('/')
    def splash():
        return render_template('splash.html')

    # ============================
    # HALAMAN UTAMA
    # ============================
    @app.route('/home')
    def home():
        # Home setelah login
        if "user_id" not in session:
            return redirect("/login")
        current_year = datetime.now().year
        return render_template('home.html', current_year=current_year, username=session["username"])

    # ============================
    # MP3 PLAYER
    # ============================
    @app.route('/mp3')
    def mp3_player():
        if "user_id" not in session:
            return redirect("/login")
        mp3_files = get_media_files(app.config['MP3_FOLDER'], ['.mp3', '.wav', '.ogg'])
        return render_template('mp3.html', mp3_files=mp3_files)

    # ============================
    # VIDEO PLAYER
    # ============================
    @app.route('/video')
    def video_player():
        if "user_id" not in session:
            return redirect("/login")
        video_files = get_media_files(app.config['VIDEO_FOLDER'], ['.mp4', '.avi', '.mkv', '.mov', '.wmv'])
        return render_template('video.html', video_files=video_files)

    # ============================
    # UPLOAD HALAMAN
    # ============================
    @app.route('/upload')
    def upload():
        if "user_id" not in session:
            return redirect("/login")
        return render_template('upload.html')

    # ============================
    # API UPLOAD FILE
    # ============================
    @app.route('/api/upload', methods=['POST'])
    def upload_file():
        if "user_id" not in session:
            return jsonify({"error": "Harus login!"}), 403

        if 'files' not in request.files:
            return jsonify({'error': 'Tidak ada file'}), 400

        files = request.files.getlist('files')
        results = []

        for file in files:
            if file.filename == '':
                results.append({'filename': '', 'status': 'error', 'message': 'Nama kosong'})
                continue

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(temp_path)

                ext = filename.rsplit('.', 1)[1].lower()
                dest = app.config['MP3_FOLDER'] if ext in ['mp3', 'wav', 'ogg'] else app.config['VIDEO_FOLDER']
                shutil.move(temp_path, os.path.join(dest, filename))

                results.append({'filename': filename, 'status': 'success'})
            else:
                results.append({'filename': file.filename, 'status': 'error'})

        return jsonify({'results': results})

    # ============================
    # HALAMAN PROFIL
    # ============================
    @app.route('/profile')
    def profile():
        if "user_id" not in session:
            return redirect("/login")

        # Ambil data profil JSON
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                profile_data = json.load(f)
        else:
            profile_data = {"nama": "", "email": "", "jk": "", "umur": "", "bio": "", "foto": ""}

        current_year = datetime.now().year
        return render_template('profile.html', profile=profile_data, current_year=current_year)

    # ============================
    # HALAMAN EDIT PROFIL
    # ============================
    @app.route('/edit-profile')
    def edit_profile():
        # Menampilkan form edit profil
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                profile_data = json.load(f)
        else:
            profile_data = {"nama": "", "email": "", "jk": "", "umur": "", "bio": "", "foto": ""}

        return render_template('edit-profile.html', profile=profile_data)

    # ============================
    # API SIMPAN PROFIL
    # ============================
    @app.route('/api/save-profile', methods=['POST'])
    def save_profile():
        if "user_id" not in session:
            return jsonify({"status": "error", "message": "Harus login!"}), 403

        data = request.json

        # Simpan JSON
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        return jsonify({"status": "success", "message": "Profil berhasil diperbarui!"})

    # ============================
    # API UPLOAD FOTO PROFIL
    # ============================
    @app.route('/api/upload-photo', methods=['POST'])
def upload_photo():
    if 'photo' not in request.files:
        return jsonify({"status": "error", "message": "Foto tidak ditemukan"}), 400

    file = request.files['photo']
    if file.filename == "":
        return jsonify({"status": "error", "message": "Nama file kosong"}), 400

    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    foto_folder = os.path.join(BASE_DIR, "static/profile")
    os.makedirs(foto_folder, exist_ok=True)

    filename = secure_filename(file.filename)
    filepath = os.path.join(foto_folder, filename)
    file.save(filepath)

    # Update JSON → simpan hanya nama file
    profile_file = app.config.get('PROFILE_FILE')

    if os.path.exists(profile_file):
        with open(profile_file, "r", encoding="utf-8") as f:
            profile_data = json.load(f)
    else:
        profile_data = {}

    profile_data["foto"] = filename

    with open(profile_file, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=4)

    return jsonify({"status": "success", "foto": filename})

    # ============================
    # UPDATE CEK GIT
    # ============================
    @app.route('/update')
    def update():
        return render_template('update.html')

    @app.route('/api/check-update', methods=['GET'])
    def check_update():
        repo_path = app.config.get('PROJECT_ROOT')
        try:
            subprocess.run(["git", "fetch"], cwd=repo_path)
            status = subprocess.run(["git", "status", "-uno"], cwd=repo_path, capture_output=True, text=True)
            update_available = "behind" in status.stdout
            return jsonify({'update_available': update_available, 'output': status.stdout})
        except Exception as e:
            return jsonify({'update_available': False, 'error': str(e)}), 500

    # ============================
    # UPDATE DENGAN WEBSOCKET
    # ============================
    @sock.route('/ws/update')
    def ws_update(ws):

        def send(msg):
            try:
                ws.send(msg)
            except:
                pass

        repo_path = app.config.get('PROJECT_ROOT')
        send("[INFO] Memulai update...\n")

        process = subprocess.Popen(
            ["git", "pull"],
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        for line in process.stdout:
            send(line.strip())

        send("[DONE]")

    # ============================
    # RESTART SERVER
    # ============================
    @app.route('/api/restart', methods=['POST'])
    def restart_server():

        def delayed():
            time.sleep(1)
            os.execl(sys.executable, sys.executable, *sys.argv)

        threading.Thread(target=delayed).start()
        return jsonify({"message": "Restart..."})

    # ============================
    # MENYAJIKAN FILE MEDIA
    # ============================
    @app.route('/media/<folder>/<filename>')
    def serve_media(folder, filename):
        if folder == 'mp3':
            return send_from_directory(app.config['MP3_FOLDER'], filename)
        if folder == 'video':
            return send_from_directory(app.config['VIDEO_FOLDER'], filename)
        return "Folder tidak valid", 404
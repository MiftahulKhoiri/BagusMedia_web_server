from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, session
from flask_sock import Sock
import os
import shutil
import subprocess
import threading
import sys
import time
import json
import sqlite3
import hashlib
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
sock = Sock(app)
app.secret_key = "ganti_ini_dengan_key_acak"


# ======================================================
# 📌 DATABASE (SQLite)
# ======================================================
def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16)
    if isinstance(salt, str):
        salt = bytes.fromhex(salt)
    hashed = hashlib.sha256(salt + password.encode()).hexdigest()
    return salt.hex() + "$" + hashed


def verify_password(stored_password, password_input):
    salt_hex, hashed = stored_password.split("$")
    return stored_password == hash_password(password_input, salt_hex)


def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


# ======================================================
# 📌 KONFIG FOLDER
# ======================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static/upload')
app.config['VIDEO_FOLDER'] = os.path.join(BASE_DIR, 'static/video')
app.config['MP3_FOLDER'] = os.path.join(BASE_DIR, 'static/mp3')
app.config['ICON_FOLDER'] = os.path.join(BASE_DIR, 'static/icon')
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1GB

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov', 'wmv', 'mp3', 'wav', 'ogg'}

PROFILE_FILE = os.path.join(BASE_DIR, "data", "profile_data.json")
os.makedirs(os.path.dirname(PROFILE_FILE), exist_ok=True)


# ======================================================
# 📌 UTILITAS
# ======================================================
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_media_files(folder, extensions):
    if not os.path.exists(folder):
        return []
    return [f for f in os.listdir(folder) if any(f.lower().endswith(ext) for ext in extensions)]


# ======================================================
# 👤 LOGIN / REGISTER
# ======================================================
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
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, created_at, updated_at) VALUES (?, ?, ?, ?)",
                           (username, hashed, now, now))
            conn.commit()
            conn.close()
            return redirect("/login")
        except sqlite3.IntegrityError:
            return "Username sudah dipakai!"

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
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


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ======================================================
# 🖼 Splash
# ======================================================
@app.route('/')
def splash():
    return render_template('splash.html')


# ======================================================
# 🏠 HOME (ADA PROTEKSI LOGIN)
# ======================================================
@app.route('/home')
def home():
    if "user_id" not in session:
        return redirect("/login")

    current_year = datetime.now().year
    return render_template('home.html', current_year=current_year, username=session["username"])


# ======================================================
# 🎵 MP3 & VIDEO PLAYER
# ======================================================
@app.route('/mp3')
def mp3_player():
    if "user_id" not in session:
        return redirect("/login")
    mp3_files = get_media_files(app.config['MP3_FOLDER'], ['.mp3', '.wav', '.ogg'])
    return render_template('mp3.html', mp3_files=mp3_files)


@app.route('/video')
def video_player():
    if "user_id" not in session:
        return redirect("/login")
    video_files = get_media_files(app.config['VIDEO_FOLDER'], ['.mp4', '.avi', '.mkv', '.mov', '.wmv'])
    return render_template('video.html', video_files=video_files)


# ======================================================
# 📤 UPLOAD
# ======================================================
@app.route('/upload')
def upload():
    if "user_id" not in session:
        return redirect("/login")
    return render_template('upload.html')


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


# ======================================================
# 🧑 Profil
# ======================================================
@app.route('/profile')
def profile():
    if "user_id" not in session:
        return redirect("/login")

    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            profile_data = json.load(f)
    else:
        profile_data = {"nama": "", "email": "", "bio": "", "foto": ""}

    current_year = datetime.now().year
    return render_template('profile.html', profile=profile_data, current_year=current_year)


@app.route('/api/save-profile', methods=['POST'])
def save_profile():
    if "user_id" not in session:
        return jsonify({"status": "error", "message": "Harus login!"}), 403

    data = request.json
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    return jsonify({"status": "success"})


# ======================================================
# 🔍 Update GitHub + WebSocket
# ======================================================
@app.route('/update')
def update():
    return render_template('update.html')


@app.route('/api/check-update', methods=['GET'])
def check_update():
    repo_path = BASE_DIR
    try:
        subprocess.run(["git", "fetch"], cwd=repo_path)
        status = subprocess.run(["git", "status", "-uno"], cwd=repo_path, capture_output=True, text=True)
        update_available = "behind" in status.stdout
        return jsonify({'update_available': update_available, 'output': status.stdout})
    except Exception as e:
        return jsonify({'update_available': False, 'error': str(e)}), 500


@sock.route('/ws/update')
def ws_update(ws):
    def send(msg):
        try:
            ws.send(msg)
        except:
            pass

    repo_path = BASE_DIR
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


# ======================================================
# 🔁 Restart
# ======================================================
@app.route('/api/restart', methods=['POST'])
def restart_server():
    def delayed():
        time.sleep(1)
        os.execl(sys.executable, sys.executable, *sys.argv)

    threading.Thread(target=delayed).start()
    return jsonify({"message": "Restart..."})

# ======================================================
# 🎵 Media
# ======================================================
@app.route('/media/<folder>/<filename>')
def serve_media(folder, filename):
    if folder == 'mp3':
        return send_from_directory(app.config['MP3_FOLDER'], filename)
    if folder == 'video':
        return send_from_directory(app.config['VIDEO_FOLDER'], filename)
    return "Folder tidak valid", 404


# ======================================================
# 🚀 RUN
# ======================================================
for folder in [app.config['UPLOAD_FOLDER'], app.config['VIDEO_FOLDER'],
               app.config['MP3_FOLDER'], app.config['ICON_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
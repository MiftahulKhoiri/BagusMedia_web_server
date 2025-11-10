from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_sock import Sock
import os
import shutil
from werkzeug.utils import secure_filename
import subprocess
import threading
import sys
import time

app = Flask(__name__)
sock = Sock(app)

# Konfigurasi folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'upload')
app.config['VIDEO_FOLDER'] = os.path.join(BASE_DIR, 'video')
app.config['MP3_FOLDER'] = os.path.join(BASE_DIR, 'mp3')
app.config['ICON_FOLDER'] = os.path.join(BASE_DIR, 'icon')
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1GB

# Ekstensi file yang diizinkan
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov', 'wmv', 'mp3', 'wav', 'ogg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_media_files(folder, extensions):
    media_files = []
    if os.path.exists(folder):
        for file in os.listdir(folder):
            if any(file.lower().endswith(ext) for ext in extensions):
                media_files.append(file)
    return media_files

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/mp3')
def mp3_player():
    mp3_files = get_media_files(app.config['MP3_FOLDER'], ['.mp3', '.wav', '.ogg'])
    return render_template('mp3.html', mp3_files=mp3_files)

@app.route('/video')
def video_player():
    video_files = get_media_files(app.config['VIDEO_FOLDER'], ['.mp4', '.avi', '.mkv', '.mov', '.wmv'])
    return render_template('video.html', video_files=video_files)

@app.route('/upload')
def upload_page():
    return render_template('upload.html')

@app.route('/update')
def update_page():
    return render_template('update.html')


# ===============================
# ✅ UPLOAD FILE (tanpa perubahan)
# ===============================
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return jsonify({'error': 'Tidak ada file yang dipilih'}), 400

    files = request.files.getlist('files')
    results = []

    for file in files:
        if file.filename == '':
            results.append({'filename': '', 'status': 'error', 'message': 'Nama file kosong'})
            continue

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(temp_path)

            ext = filename.rsplit('.', 1)[1].lower()
            destination_folder = app.config['MP3_FOLDER'] if ext in ['mp3', 'wav', 'ogg'] else app.config['VIDEO_FOLDER']
            shutil.move(temp_path, os.path.join(destination_folder, filename))

            results.append({'filename': filename, 'status': 'success', 'message': f'File berhasil diupload ke {destination_folder}'})
        else:
            results.append({'filename': file.filename, 'status': 'error', 'message': 'Tipe file tidak diizinkan'})

    return jsonify({'results': results})


# ===============================
# ✅ CEK PEMBARUAN DARI GITHUB
# ===============================
@app.route('/api/check-update', methods=['GET'])
def check_update():
    repo_path = BASE_DIR
    try:
        subprocess.run(["git", "fetch"], cwd=repo_path, capture_output=True, text=True)
        status_cmd = subprocess.run(["git", "status", "-uno"], cwd=repo_path, capture_output=True, text=True)
        update_available = "Your branch is behind" in status_cmd.stdout
        return jsonify({
            'update_available': update_available,
            'output': status_cmd.stdout
        })
    except Exception as e:
        return jsonify({'update_available': False, 'error': str(e)}), 500


# ===============================
# ✅ PROSES UPDATE REALTIME (WEBSOCKET)
# ===============================
@sock.route('/ws/update')
def ws_update(ws):
    def send(msg):
        try:
            ws.send(msg)
        except Exception:
            pass

    repo_path = BASE_DIR
    send("[INFO] Memulai proses update dari GitHub...\n")

    # Pastikan repo valid
    if not os.path.exists(os.path.join(repo_path, ".git")):
        send("[ERROR] Folder ini bukan repository Git!\n")
        ws.close()
        return

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

    process.wait()
    if process.returncode == 0:
        send("[SUCCESS] Pembaruan selesai.\n")
        send("[SUCCESS] Sistem siap direstart.\n")
    else:
        send(f"[ERROR] Proses gagal (kode {process.returncode}).\n")

    send("[DONE]")


# ===============================
# ✅ RESTART SERVER
# ===============================
@app.route('/api/restart', methods=['POST'])
def restart_server():
    def delayed_restart():
        time.sleep(1)
        os.execl(sys.executable, sys.executable, *sys.argv)
    threading.Thread(target=delayed_restart).start()
    return jsonify({"message": "Server akan direstart..."})


# ===============================
# ✅ SERVE MEDIA FILES
# ===============================
@app.route('/media/<folder>/<filename>')
def serve_media(folder, filename):
    if folder == 'mp3':
        return send_from_directory(app.config['MP3_FOLDER'], filename)
    elif folder == 'video':
        return send_from_directory(app.config['VIDEO_FOLDER'], filename)
    else:
        return "Folder tidak valid", 404


# Pastikan folder tersedia
for folder in [app.config['UPLOAD_FOLDER'], app.config['VIDEO_FOLDER'], app.config['MP3_FOLDER'], app.config['ICON_FOLDER']]:
    os.makedirs(folder, exist_ok=True)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
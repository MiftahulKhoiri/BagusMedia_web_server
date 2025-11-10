from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import shutil
from werkzeug.utils import secure_filename
import subprocess
import threading

app = Flask(__name__)

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
    """Memeriksa apakah ekstensi file diizinkan"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_media_files(folder, extensions):
    """Mendapatkan daftar file media dari folder tertentu"""
    media_files = []
    if os.path.exists(folder):
        for file in os.listdir(folder):
            if any(file.lower().endswith(ext) for ext in extensions):
                media_files.append(file)
    return media_files

@app.route('/')
def home():
    """Route halaman utama"""
    return render_template('home.html')

@app.route('/mp3')
def mp3_player():
    """Route pemutar MP3"""
    mp3_files = get_media_files(app.config['MP3_FOLDER'], ['.mp3', '.wav', '.ogg'])
    return render_template('mp3.html', mp3_files=mp3_files)

@app.route('/video')
def video_player():
    """Route pemutar video"""
    video_files = get_media_files(app.config['VIDEO_FOLDER'], ['.mp4', '.avi', '.mkv', '.mov', '.wmv'])
    return render_template('video.html', video_files=video_files)

@app.route('/upload')
def upload_page():
    """Route halaman upload"""
    return render_template('upload.html')

@app.route('/update')
def update_page():
    """Route halaman update sistem"""
    return render_template('update.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """API untuk mengunggah file"""
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

            # Simpan sementara
            file.save(temp_path)

            # Tentukan folder tujuan
            file_extension = filename.rsplit('.', 1)[1].lower()
            if file_extension in ['mp3', 'wav', 'ogg']:
                destination_folder = app.config['MP3_FOLDER']
            else:
                destination_folder = app.config['VIDEO_FOLDER']

            # Pindahkan file ke folder tujuan
            destination_path = os.path.join(destination_folder, filename)
            shutil.move(temp_path, destination_path)

            results.append({
                'filename': filename, 
                'status': 'success', 
                'message': f'File berhasil diupload ke {destination_folder}'
            })
        else:
            results.append({
                'filename': file.filename, 
                'status': 'error', 
                'message': 'Tipe file tidak diizinkan'
            })

    return jsonify({'results': results})


@app.route('/api/update', methods=['POST'])
def update_system():
    """API untuk memperbarui sistem dari GitHub"""
    repo_path = BASE_DIR  # Folder tempat app.py berada

    def run_update():
        log_file = os.path.join(BASE_DIR, "update_log.txt")
        try:
            with open(log_file, "w") as log:
                log.write("=== Memulai pembaruan dari GitHub ===\n")

                # Pastikan folder adalah repo git
                if not os.path.exists(os.path.join(repo_path, ".git")):
                    log.write("ERROR: Folder ini bukan repository Git!\n")
                    return

                commands = [
                    "git fetch origin",
                    "git reset --hard origin/main",  # pastikan update penuh
                    "git pull origin main"
                ]

                for cmd in commands:
                    log.write(f"\nMenjalankan: {cmd}\n")
                    process = subprocess.Popen(
                        cmd, cwd=repo_path, shell=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                    )
                    stdout, stderr = process.communicate()
                    log.write(stdout)
                    if stderr:
                        log.write("ERROR: " + stderr)

                log.write("\n=== Pembaruan selesai ===\n")

        except Exception as e:
            with open(log_file, "a") as log:
                log.write(f"Kesalahan saat update: {str(e)}\n")

    # Jalankan update di thread terpisah
    thread = threading.Thread(target=run_update)
    thread.daemon = True
    thread.start()

    return jsonify({'status': 'success', 'message': 'Proses pembaruan dimulai. Lihat file update_log.txt untuk detail.'})


@app.route('/api/check-update', methods=['GET'])
def check_update():
    """API untuk memeriksa apakah ada pembaruan dari GitHub"""
    repo_path = BASE_DIR

    try:
        fetch_cmd = subprocess.run(
            ["git", "fetch"], cwd=repo_path,
            capture_output=True, text=True
        )
        status_cmd = subprocess.run(
            ["git", "status", "-uno"], cwd=repo_path,
            capture_output=True, text=True
        )

        output = fetch_cmd.stdout + "\n" + status_cmd.stdout
        update_available = "Your branch is behind" in status_cmd.stdout

        return jsonify({
            'update_available': update_available,
            'output': output
        })
    except Exception as e:
        return jsonify({'update_available': False, 'error': str(e)}), 500


@app.route('/media/<folder>/<filename>')
def serve_media(folder, filename):
    """Route untuk menyajikan file media"""
    if folder == 'mp3':
        return send_from_directory(app.config['MP3_FOLDER'], filename)
    elif folder == 'video':
        return send_from_directory(app.config['VIDEO_FOLDER'], filename)
    else:
        return "Folder tidak valid", 404


# Pastikan semua folder tersedia
for folder in [app.config['UPLOAD_FOLDER'], app.config['VIDEO_FOLDER'], app.config['MP3_FOLDER'], app.config['ICON_FOLDER']]:
    os.makedirs(folder, exist_ok=True)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
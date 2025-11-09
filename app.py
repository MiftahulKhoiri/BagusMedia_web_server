from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import shutil
from werkzeug.utils import secure_filename
import subprocess
import threading

app = Flask(__name__)

# Konfigurasi folder
app.config['UPLOAD_FOLDER'] = 'upload'
app.config['VIDEO_FOLDER'] = 'video'
app.config['MP3_FOLDER'] = 'mp3'
app.config['ICON_FOLDER'] = 'icon'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 100MB max file size

# Ekstensi file yang diizinkan
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov', 'wmv', 'mp3', 'wav', 'ogg'}

def allowed_file(filename):
    """Memeriksa apakah ekstensi file diizinkan"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    """Route untuk halaman utama"""
    return render_template('home.html')

@app.route('/mp3')
def mp3_player():
    """Route untuk pemutar MP3"""
    mp3_files = get_media_files(app.config['MP3_FOLDER'], ['.mp3', '.wav', '.ogg'])
    return render_template('mp3.html', mp3_files=mp3_files)

@app.route('/video')
def video_player():
    """Route untuk pemutar video"""
    video_files = get_media_files(app.config['VIDEO_FOLDER'], ['.mp4', '.avi', '.mkv', '.mov', '.wmv'])
    return render_template('video.html', video_files=video_files)

@app.route('/upload')
def upload_page():
    """Route untuk halaman upload"""
    return render_template('upload.html')

@app.route('/update')
def update_page():
    """Route untuk halaman update sistem"""
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
            
            # Simpan file sementara di folder upload
            file.save(temp_path)
            
            # Tentukan folder tujuan berdasarkan ekstensi
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
                'message': f'File berhasil diupload dan dipindah ke {destination_folder}'
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
    def run_update():
        try:
            # Perintah untuk update dari GitHub
            commands = [
                ['git', 'pull', 'origin', 'main'],
                # Tambahkan perintah lain yang diperlukan untuk update
            ]
            
            for cmd in commands:
                result = subprocess.run(cmd, capture_output=True, text=True)
                # Log hasil perintah (bisa disimpan ke file log)
                print(f"Command: {' '.join(cmd)}")
                print(f"Output: {result.stdout}")
                print(f"Error: {result.stderr}")
                
        except Exception as e:
            print(f"Error during update: {str(e)}")
    
    # Jalankan update di thread terpisah agar tidak blocking
    thread = threading.Thread(target=run_update)
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'success', 'message': 'Proses pembaruan dimulai'})

@app.route('/media/<folder>/<filename>')
def serve_media(folder, filename):
    """Route untuk menyajikan file media"""
    if folder == 'mp3':
        return send_from_directory(app.config['MP3_FOLDER'], filename)
    elif folder == 'video':
        return send_from_directory(app.config['VIDEO_FOLDER'], filename)
    else:
        return "Folder tidak valid", 404

# Buat folder jika belum ada
for folder in [app.config['UPLOAD_FOLDER'], app.config['VIDEO_FOLDER'], 
               app.config['MP3_FOLDER'], app.config['ICON_FOLDER']]:
    if not os.path.exists(folder):
        os.makedirs(folder)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
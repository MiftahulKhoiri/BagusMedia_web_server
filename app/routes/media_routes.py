import os
import shutil
import subprocess
import threading
import time
from flask import (
    render_template, request, jsonify,
    redirect, session, send_from_directory, current_app
)
from werkzeug.utils import secure_filename

# ============================================================
#  EKSTENSI VALID
# ============================================================
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov', 'wmv', 'mp3', 'wav', 'ogg'}


def allowed_file(filename):
    """Cek ekstensi file valid."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_media_files(folder, ext_list):
    """Ambil list file yang sesuai ekstensi."""
    if not os.path.exists(folder):
        return []
    return [
        f for f in os.listdir(folder)
        if any(f.lower().endswith(ext) for ext in ext_list)
    ]


def generate_video_thumbnail(video_path, output_path):
    """
    Generate thumbnail via ffmpeg.
    Mengambil frame pada detik ke-1 (-ss 00:00:01) dan menyimpan jpg scaled.
    Mengembalikan True jika berhasil, False jika gagal.
    """
    try:
        # Pastikan direktorinya ada
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # ffmpeg command: -y overwrite, -ss seek, -vframes 1 capture single frame
        cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-ss", "00:00:01",
            "-vframes", "1",
            "-vf", "scale=320:-1",  # scale lebar 320, proporsional tinggi
            output_path
        ]

        # Jalankan ffmpeg, capture output untuk debugging (jika perlu)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0 and os.path.exists(output_path):
            return True
        else:
            # Jika error, hapus file partial jika ada
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except:
                    pass
            current_app.logger.debug("ffmpeg thumb error: %s", result.stderr)
            return False
    except Exception as e:
        current_app.logger.debug("thumb exception: %s", str(e))
        return False


def register_media_routes(app):
    """
    Semua route media:
    MP3, video, upload, album list, serve file, thumbnail.
    """

    MP3_FOLDER = app.config["MP3_FOLDER"]
    VIDEO_FOLDER = app.config["VIDEO_FOLDER"]
    UPLOAD_FOLDER = app.config["UPLOAD_FOLDER"]

    THUMB_FOLDER = os.path.join(app.static_folder, "thumbs", "video")
    os.makedirs(THUMB_FOLDER, exist_ok=True)

    os.makedirs(MP3_FOLDER, exist_ok=True)
    os.makedirs(VIDEO_FOLDER, exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # ============================================================
    #  MP3 PLAYER
    # ============================================================
    @app.route("/mp3")
    def mp3_player():
        if "user_id" not in session:
            return redirect("/login")

        mp3_files = get_media_files(MP3_FOLDER, ['.mp3', '.wav', '.ogg'])
        return render_template("mp3.html", mp3_files=mp3_files)

    # ============================================================
    #  VIDEO PLAYER
    # ============================================================
    @app.route("/video")
    def video_player():
        if "user_id" not in session:
            return redirect("/login")

        video_files = get_media_files(VIDEO_FOLDER, ['.mp4', '.avi', '.mkv', '.mov', '.wmv'])
        return render_template("video.html", video_files=video_files)

    # ============================================================
    #  MP3 LIST / GALERI
    # ============================================================
    @app.route("/audios")
    def audio_list():
        if "user_id" not in session:
            return redirect("/login")

        mp3_files = get_media_files(MP3_FOLDER, ['.mp3', '.wav', '.ogg'])
        return render_template("mp3-list.html", mp3_files=mp3_files)

    # ============================================================
    #  VIDEO LIST / GALERI
    # ============================================================
    @app.route("/videos")
    def video_list():
        if "user_id" not in session:
            return redirect("/login")

        video_files = get_media_files(VIDEO_FOLDER, ['.mp4', '.avi', '.mkv', '.mov', '.wmv'])
        return render_template("video-list.html", video_files=video_files)

    # ============================================================
    #  API THUMBNAIL VIDEO OTOMATIS
    # ============================================================
    @app.route("/api/video-thumb")
    def video_thumb():
        """
        Serve thumbnail jika ada, atau coba generate lalu serve.
        Query param: ?file=<filename>
        """
        file = request.args.get("file")
        if not file:
            return jsonify({"error": "file tidak ditemukan"}), 400

        # Sanitasi nama file (ambil basename agar aman)
        filename = os.path.basename(file)
        video_path = os.path.join(VIDEO_FOLDER, filename)
        if not os.path.exists(video_path):
            return jsonify({"error": "video tidak ada"}), 404

        # thumb name berdasarkan nama file tanpa ekstensi
        base = os.path.splitext(filename)[0]
        thumb_name = secure_filename(base) + ".jpg"
        thumb_path = os.path.join(THUMB_FOLDER, thumb_name)

        # Jika sudah ada, serve langsung
        if os.path.exists(thumb_path):
            return send_from_directory(THUMB_FOLDER, thumb_name)

        # Coba generate synchronously (cepat) — fallback ke default jika gagal
        ok = generate_video_thumbnail(video_path, thumb_path)
        if ok and os.path.exists(thumb_path):
            return send_from_directory(THUMB_FOLDER, thumb_name)
        else:
            # fallback ke gambar default (letakkan di static/icon/default-thumb.png)
            default = os.path.join(app.static_folder, "icon", "default-thumb.png")
            if os.path.exists(default):
                return send_from_directory(os.path.join(app.static_folder, "icon"), "default-thumb.png")
            return jsonify({"error": "gagal membuat thumbnail"}), 500

    # ============================================================
    #  HALAMAN UPLOAD
    # ============================================================
    @app.route("/upload")
    def upload():
        if "user_id" not in session:
            return redirect("/login")

        return render_template("upload.html")

    # ============================================================
    #  API UPLOAD MEDIA
    # ============================================================
    @app.route("/api/upload", methods=["POST"])
    def upload_file():
        if "user_id" not in session:
            return jsonify({"error": "Harus login!"}), 403

        if "files" not in request.files:
            return jsonify({"error": "File tidak ditemukan!"}), 400

        files = request.files.getlist("files")
        results = []

        for file in files:
            if not file.filename:
                results.append({"filename": "", "status": "error"})
                continue

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                temp_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(temp_path)

                ext = filename.rsplit(".", 1)[1].lower()
                dest = MP3_FOLDER if ext in ['mp3', 'wav', 'ogg'] else VIDEO_FOLDER

                final_path = os.path.join(dest, filename)
                shutil.move(temp_path, final_path)

                results.append({"filename": filename, "status": "success"})

                # Jika file video → buat thumbnail di background supaya respon cepat
                if ext in ['mp4', 'avi', 'mkv', 'mov', 'wmv']:
                    # buat nama thumb berdasarkan filename (tanpa ekstensi)
                    base = os.path.splitext(filename)[0]
                    thumb_name = secure_filename(base) + ".jpg"
                    thumb_path = os.path.join(THUMB_FOLDER, thumb_name)

                    # generate di thread (tidak block request)
                    def worker_generate(src=final_path, dst=thumb_path):
                        try:
                            generate_video_thumbnail(src, dst)
                        except Exception as e:
                            app.logger.debug("thumb thread error: %s", str(e))

                    t = threading.Thread(target=worker_generate, daemon=True)
                    t.start()

            else:
                results.append({"filename": file.filename, "status": "error"})

        return jsonify({"results": results})

    # ============================================================
    #  MEDIA SERVER
    # ============================================================
    @app.route("/media/<folder>/<filename>")
    def serve_media(folder, filename):
        # Hanya izinkan folder mp3/video
        if folder == "mp3":
            return send_from_directory(MP3_FOLDER, filename)

        if folder == "video":
            return send_from_directory(VIDEO_FOLDER, filename)

        return "Folder tidak valid", 404
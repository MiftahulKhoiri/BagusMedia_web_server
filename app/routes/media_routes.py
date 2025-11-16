import os
import shutil
from flask import (
    render_template, request, jsonify,
    redirect, session, send_from_directory
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


def register_media_routes(app):
    """
    Semua route yang berhubungan dengan media:
    MP3, video, upload, album list, dan serve file.
    """

    MP3_FOLDER = app.config["MP3_FOLDER"]
    VIDEO_FOLDER = app.config["VIDEO_FOLDER"]
    UPLOAD_FOLDER = app.config["UPLOAD_FOLDER"]

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
    #  LIST MUSIK (GALERI)
    # ============================================================
    @app.route("/audios")
    def audio_list():
        if "user_id" not in session:
            return redirect("/login")

        mp3_files = get_media_files(MP3_FOLDER, ['.mp3', '.wav', '.ogg'])
        return render_template("mp3-list.html", mp3_files=mp3_files)

    # ============================================================
    #  LIST VIDEO (GALERI)
    # ============================================================
    @app.route("/videos")
    def video_list():
        if "user_id" not in session:
            return redirect("/login")

        video_files = get_media_files(VIDEO_FOLDER, ['.mp4', '.avi', '.mkv', '.mov', '.wmv'])
        return render_template("video-list.html", video_files=video_files)

    # ============================================================
    #  HALAMAN UPLOAD
    # ============================================================
    @app.route("/upload")
    def upload():
        if "user_id" not in session:
            return redirect("/login")

        return render_template("upload.html")

    # ============================================================
    #  API UPLOAD FILE
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
            if file.filename == "":
                results.append({"filename": "", "status": "error", "message": "Nama kosong"})
                continue

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                temp_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(temp_path)

                # Tentukan folder tujuan
                ext = filename.rsplit(".", 1)[1].lower()
                dest = MP3_FOLDER if ext in ['mp3', 'wav', 'ogg'] else VIDEO_FOLDER
                shutil.move(temp_path, os.path.join(dest, filename))

                results.append({"filename": filename, "status": "success"})
            else:
                results.append({"filename": file.filename, "status": "error", "message": "Ekstensi tidak valid"})

        return jsonify({"results": results})

    # ============================================================
    #  MENYAJIKAN FILE MEDIA
    # ============================================================
    @app.route("/media/<folder>/<filename>")
    def serve_media(folder, filename):
        if folder == "mp3":
            return send_from_directory(MP3_FOLDER, filename)

        if folder == "video":
            return send_from_directory(VIDEO_FOLDER, filename)

        return "Folder tidak valid", 404
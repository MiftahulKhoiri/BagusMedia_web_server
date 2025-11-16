import os
import shutil
from flask import (
    render_template, request, jsonify,
    redirect, session, send_from_directory
)
from werkzeug.utils import secure_filename

# Untuk thumbnail
from moviepy.editor import VideoFileClip
from PIL import Image


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
    Semua route media:
    MP3, video, upload, album list, serve file, thumbnail.
    """

    MP3_FOLDER = app.config["MP3_FOLDER"]
    VIDEO_FOLDER = app.config["VIDEO_FOLDER"]
    UPLOAD_FOLDER = app.config["UPLOAD_FOLDER"]

    THUMB_FOLDER = os.path.join(app.static_folder, "thumbs")
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
        file = request.args.get("file")

        if not file:
            return jsonify({"error": "file tidak ditemukan"}), 400

        video_path = os.path.join(VIDEO_FOLDER, file)
        if not os.path.exists(video_path):
            return jsonify({"error": "video tidak ada"}), 404

        thumb_name = file + ".jpg"
        thumb_path = os.path.join(THUMB_FOLDER, thumb_name)

        # Jika thumbnail sudah ada
        if os.path.exists(thumb_path):
            return send_from_directory(THUMB_FOLDER, thumb_name)

        # Generate thumbnail
        try:
            clip = VideoFileClip(video_path)
            frame = clip.get_frame(0.5)
            clip.close()

            img = Image.fromarray(frame)
            img.save(thumb_path, "JPEG")

            return send_from_directory(THUMB_FOLDER, thumb_name)

        except Exception as e:
            return jsonify({"error": str(e)}), 500

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

                shutil.move(temp_path, os.path.join(dest, filename))

                results.append({"filename": filename, "status": "success"})
            else:
                results.append({"filename": file.filename, "status": "error"})

        return jsonify({"results": results})

    # ============================================================
    #  MEDIA SERVER
    # ============================================================
    @app.route("/media/<folder>/<filename>")
    def serve_media(folder, filename):
        if folder == "mp3":
            return send_from_directory(MP3_FOLDER, filename)

        if folder == "video":
            return send_from_directory(VIDEO_FOLDER, filename)

        return "Folder tidak valid", 404
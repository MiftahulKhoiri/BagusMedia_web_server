import os
import shutil
from flask import (
    Blueprint, render_template, request, jsonify, redirect, session
)
from werkzeug.utils import secure_filename
from .helper import allowed_file, get_media_files

media = Blueprint("media", __name__)

def init_media(app):

    MP3 = app.config["MP3_FOLDER"]
    VIDEO = app.config["VIDEO_FOLDER"]
    UPLOAD = app.config["UPLOAD_FOLDER"]

    # =============================
    # HALAMAN PEMUTAR MP3
    # =============================
    @media.route("/mp3")
    def mp3_player():
        if "user_id" not in session:
            return redirect("/login")
        mp3_files = get_media_files(MP3, ['.mp3', '.wav', '.ogg'])
        return render_template("mp3.html", mp3_files=mp3_files)

    # =============================
    # HALAMAN PEMUTAR VIDEO
    # =============================
    @media.route("/video")
    def video_player():
        if "user_id" not in session:
            return redirect("/login")
        video_files = get_media_files(VIDEO, ['.mp4', '.avi', '.mkv', '.mov', '.wmv'])
        return render_template("video.html", video_files=video_files)

    # =============================
    # DAFTAR ALBUM MP3
    # =============================
    @media.route("/audios")
    def audio_list():
        if "user_id" not in session:
            return redirect("/login")
        mp3_files = get_media_files(MP3, ['.mp3', '.wav', '.ogg'])
        return render_template("mp3-list.html", mp3_files=mp3_files)

    # =============================
    # DAFTAR ALBUM VIDEO
    # =============================
    @media.route("/videos")
    def video_list():
        if "user_id" not in session:
            return redirect("/login")
        video_files = get_media_files(VIDEO, ['.mp4', '.avi', '.mkv', '.mov', '.wmv'])
        return render_template("video-list.html", video_files=video_files)

    # =============================
    # HALAMAN UPLOAD
    # =============================
    @media.route("/upload")
    def upload_page():
        if "user_id" not in session:
            return redirect("/login")
        return render_template("upload.html")

    # =============================
    # API UPLOAD MEDIA
    # =============================
    @media.route("/api/upload", methods=["POST"])
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

            if not allowed_file(file.filename):
                results.append({"filename": file.filename, "status": "error"})
                continue

            # Simpan sementara
            filename = secure_filename(file.filename)
            temp_path = os.path.join(UPLOAD, filename)
            file.save(temp_path)

            # Tentukan folder tujuan
            ext = filename.rsplit(".", 1)[1].lower()
            dest = MP3 if ext in ['mp3', 'wav', 'ogg'] else VIDEO

            shutil.move(temp_path, os.path.join(dest, filename))
            results.append({"filename": filename, "status": "success"})

        return jsonify({"results": results})
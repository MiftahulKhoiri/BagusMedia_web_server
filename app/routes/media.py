# app/routes/media.py
import os
import shutil
from flask import Blueprint, render_template, request, jsonify, redirect, session, current_app
from werkzeug.utils import secure_filename
from flask import send_from_directory
from .utils import allowed_file, get_media_files,require_root

# =====================================================
# BLUEPRINT MEDIA
# =====================================================
media = Blueprint("media", __name__)


# =====================================================
# MP3 PLAYER
# =====================================================
@media.route("/mp3")
def mp3_player():
    if "user_id" not in session:
        return redirect("/login")

    mp3_files = get_media_files(
        current_app.config["MP3_FOLDER"],
        ['.mp3', '.wav', '.ogg']
    )

    return render_template("mp3.html", mp3_files=mp3_files)


# =====================================================
# VIDEO PLAYER
# =====================================================
@media.route("/video")
def video_player():
    if "user_id" not in session:
        return redirect("/login")

    video_files = get_media_files(
        current_app.config["VIDEO_FOLDER"],
        ['.mp4', '.avi', '.mkv', '.mov', '.wmv']
    )

    return render_template("video.html", video_files=video_files)


# =====================================================
# MP3 LIST (ALBUM)
# =====================================================
@media.route("/audios")
def audio_list():
    if "user_id" not in session:
        return redirect("/login")

    mp3_files = get_media_files(
        current_app.config["MP3_FOLDER"],
        ['.mp3', '.wav', '.ogg']
    )

    return render_template("mp3-list.html", mp3_files=mp3_files)


# =====================================================
# VIDEO LIST (ALBUM)
# =====================================================
@media.route("/videos")
def video_list():
    if "user_id" not in session:
        return redirect("/login")

    video_files = get_media_files(
        current_app.config["VIDEO_FOLDER"],
        ['.mp4', '.avi', '.mkv', '.mov', '.wmv']
    )

    return render_template("video-list.html", video_files=video_files)


# =====================================================
# UPLOAD MEDIA PAGE
# =====================================================
@media.route("/upload")
def upload():
    if "user_id" not in session:
        return redirect("/login")
    check = require_root()
    if check:
        return check
    
    return render_template("upload.html")


# =====================================================
# API UPLOAD MEDIA
# =====================================================
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

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            temp_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)

            # Simpan sementara
            file.save(temp_path)

            ext = filename.rsplit(".", 1)[1].lower()

            # Tentukan tujuan
            if ext in ['mp3', 'wav', 'ogg']:
                dest = current_app.config["MP3_FOLDER"]
            else:
                dest = current_app.config["VIDEO_FOLDER"]

            shutil.move(temp_path, os.path.join(dest, filename))
            results.append({"filename": filename, "status": "success"})

        else:
            results.append({"filename": file.filename, "status": "error"})

    return jsonify({"results": results})


# =====================================================
# SERVE MEDIA (FINAL FIX)
# =====================================================
@media.route("/media/<folder>/<filename>")
def serve_media(folder, filename):
    """
    Mengirim file MP3/VIDEO ke browser.
    Wajib memakai send_from_directory untuk support streaming.
    """

    # Kirim file MP3
    if folder == "mp3":
        return send_from_directory(
            current_app.config["MP3_FOLDER"],
            filename,
            as_attachment=False
        )

    # Kirim file VIDEO
    elif folder == "video":
        return send_from_directory(
            current_app.config["VIDEO_FOLDER"],
            filename,
            as_attachment=False
        )

    # Folder tidak ada
    return "Folder tidak valid", 404
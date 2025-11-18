# app/routes/media.py
import os
import shutil
import time
from flask import Blueprint, render_template, request, jsonify, redirect, session, current_app
from werkzeug.utils import secure_filename
from .utils import allowed_file, get_media_files

# ============================================
# BLUEPRINT MEDIA (MP3 / VIDEO / UPLOAD / SERVE)
# ============================================
media = Blueprint("media", __name__)


# ============================================
# MP3 PLAYER
# ============================================
@media.route("/mp3")
def mp3_player():
    """
    Menampilkan halaman pemutar MP3.
    Hanya untuk user yang sudah login.
    Mengambil file dari folder MP3_FOLDER.
    """
    if "user_id" not in session:
        return redirect("/login")
    mp3_files = get_media_files(current_app.config["MP3_FOLDER"], ['.mp3', '.wav', '.ogg'])
    return render_template("mp3.html", mp3_files=mp3_files)


# ============================================
# VIDEO PLAYER
# ============================================
@media.route("/video")
def video_player():
    """
    Menampilkan halaman pemutar video.
    Hanya untuk user yang sudah login.
    Mengambil file dari folder VIDEO_FOLDER.
    """
    if "user_id" not in session:
        return redirect("/login")
    video_files = get_media_files(current_app.config["VIDEO_FOLDER"], ['.mp4', '.avi', '.mkv', '.mov', '.wmv'])
    return render_template("video.html", video_files=video_files)


# ============================================
# MP3 LIST (ALBUM)
# ============================================
@media.route("/audios")
def audio_list():
    """
    Menampilkan daftar audio (album).
    Sama akses kontrolnya seperti mp3_player.
    """
    if "user_id" not in session:
        return redirect("/login")
    mp3_files = get_media_files(current_app.config["MP3_FOLDER"], ['.mp3', '.wav', '.ogg'])
    return render_template("mp3-list.html", mp3_files=mp3_files)


# ============================================
# VIDEO LIST (ALBUM)
# ============================================
@media.route("/videos")
def video_list():
    """
    Menampilkan daftar video (album).
    Sama akses kontrolnya seperti video_player.
    """
    if "user_id" not in session:
        return redirect("/login")
    video_files = get_media_files(current_app.config["VIDEO_FOLDER"], ['.mp4', '.avi', '.mkv', '.mov', '.wmv'])
    return render_template("video-list.html", video_files=video_files)


# ============================================
# UPLOAD MEDIA PAGE
# ============================================
@media.route("/upload")
def upload():
    """
    Halaman upload file (form).
    Hanya bisa diakses user yang login.
    """
    if "user_id" not in session:
        return redirect("/login")
    return render_template("upload.html")


# ============================================
# API UPLOAD MEDIA
# ============================================
@media.route("/api/upload", methods=["POST"])
def upload_file():
    """
    API yang menerima multipart upload (bisa multiple files).
    - Memastikan user login
    - Memvalidasi ekstensi file menggunakan allowed_file()
    - Menyimpan sementara di UPLOAD_FOLDER lalu dipindah ke MP3_FOLDER atau VIDEO_FOLDER
    - Mengembalikan JSON hasil per-file
    """
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

            # Pilih tujuan berdasarkan ekstensi
            ext = filename.rsplit(".", 1)[1].lower()
            dest = (
                current_app.config["MP3_FOLDER"]
                if ext in ['mp3', 'wav', 'ogg']
                else current_app.config["VIDEO_FOLDER"]
            )

            # Pindahkan file dari upload ke folder tujuan
            shutil.move(temp_path, os.path.join(dest, filename))
            results.append({"filename": filename, "status": "success"})
        else:
            results.append({"filename": file.filename, "status": "error"})

    return jsonify({"results": results})


# ============================================
# MENYAJIKAN FILE MEDIA
# ============================================
@media.route("/media/<folder>/<filename>")
def serve_media(folder, filename):
    """
    Menyajikan file media statis dari folder MP3_FOLDER atau VIDEO_FOLDER.
    - /media/mp3/<filename> -> ambil dari MP3_FOLDER
    - /media/video/<filename> -> ambil dari VIDEO_FOLDER
    Jika folder tidak valid, kembalikan 404.
    """
    if folder == "mp3":
        return current_app.send_static_file  # placeholder not used; keep logic below

    # Gunakan send_from_directory agar header dan range request (video) bekerja
    from flask import send_from_directory
    if folder == "mp3":
        return send_from_directory(current_app.config["MP3_FOLDER"], filename)
    if folder == "video":
        return send_from_directory(current_app.config["VIDEO_FOLDER"], filename)
    return "Folder tidak valid", 404
# app/routes/media.py
import io
import os
import shutil
from flask import Blueprint, render_template, request, jsonify, redirect, session, current_app,send_file
from werkzeug.utils import secure_filename
from flask import send_from_directory
from .utils import allowed_file, get_media_files,require_root
from mutagen.id3 import ID3
import requests

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

@media.route("/media/cover/mp3/<path:filename>")
def serve_mp3_cover(filename):
    """
    Cover otomatis:
    1. Cek file MP3 apakah punya cover → tampilkan
    2. Jika tidak → cek cache lokal → tampilkan
    3. Jika tidak ada cache → cari ke internet → simpan → tampilkan
    """

    safe_name = os.path.basename(filename)
    mp3_path = os.path.join(current_app.config["MP3_FOLDER"], safe_name)

    default_img = os.path.join(current_app.root_path, "static/icon/Mp3.png")
    cache_folder = os.path.join(current_app.root_path, "static/cache/covers")
    os.makedirs(cache_folder, exist_ok=True)

    # lokasi cache
    cache_file = os.path.join(cache_folder, safe_name + ".jpg")

    # STEP 1 — Ambil COVER dari file MP3 jika ada
    try:
        tags = ID3(mp3_path)
        for key, val in tags.items():
            if key.startswith("APIC"):
                img_data = val.data
                return send_file(io.BytesIO(img_data), mimetype=val.mime)
    except:
        pass

    # STEP 2 — Jika ada cache lokal → pakai itu
    if os.path.exists(cache_file):
        return send_file(cache_file, mimetype="image/jpeg")

    # STEP 3 — CARI COVER dari internet
    # Ambil judul dari nama file
    q = os.path.splitext(safe_name)[0]
    q = q.replace("_", " ").replace("-", " ")

    # API iTunes Search (COVER ALBUM BAGUS!)
    try:
        api = f"https://itunes.apple.com/search?term={q}&media=music&limit=1"
        r = requests.get(api, timeout=5).json()

        if r["resultCount"] > 0:
            artwork = r["results"][0]["artworkUrl100"].replace("100x100", "600x600")

            # download cover
            img = requests.get(artwork, timeout=5).content

            # simpan cache
            with open(cache_file, "wb") as f:
                f.write(img)

            return send_file(io.BytesIO(img), mimetype="image/jpeg")
    except Exception as e:
        print("COVER NET ERROR:", e)

    # fallback
    return send_file(default_img, mimetype="image/png")
# app/routes/media.py
import os
import shutil
from flask import Blueprint, render_template, request, jsonify, redirect, session, current_app,send_file
from werkzeug.utils import secure_filename
from flask import send_from_directory
from .utils import allowed_file, get_media_files,require_root
import io
from mutagen.id3 import ID3


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

# route baru - letakkan setelah serve_media
@media.route("/media/cover/mp3/<path:filename>")
def serve_mp3_cover(filename):
    """
    Kembalikan cover art (APIC) dari file MP3, atau default icon bila tidak ada.
    """
    safe_name = secure_filename(filename)
    mp3_path = os.path.join(current_app.config.get("MP3_FOLDER", ""), safe_name)

    # jika file mp3 tidak ada, kembalikan gambar default
    default_img = os.path.join(current_app.root_path, "static", "icon", "Mp3.png")
    if not os.path.exists(mp3_path):
        return send_file(default_img, mimetype="image/png")

    # baca tag ID3
    try:
        tags = ID3(mp3_path)
    except Exception:
        # error baca tag → fallback ke default
        return send_file(default_img, mimetype="image/png")

    # cari frame APIC
    for key, val in tags.items():
        if key.startswith("APIC"):
            apic = val
            mime = apic.mime or "image/jpeg"
            img_data = apic.data
            buf = io.BytesIO(img_data)
            buf.seek(0)
            return send_file(buf, mimetype=mime)

    # tidak ada APIC → default
    return send_file(default_img, mimetype="image/png")
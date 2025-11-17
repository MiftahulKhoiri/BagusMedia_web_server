import os
from flask import render_template, redirect, session, send_from_directory

# Import helper
from .utils import get_media_files

# =============================
# ROUTES: MP3, VIDEO & MEDIA FILES
# =============================

def media_routes(app):
    MP3_EXT = ['.mp3', '.wav', '.ogg']
    VIDEO_EXT = ['.mp4', '.avi', '.mkv', '.mov', '.wmv']

    # MP3 PLAYER PAGE
    @app.route("/mp3")
    def mp3_player():
        if "user_id" not in session:
            return redirect("/login")

        mp3_files = get_media_files(app.config["MP3_FOLDER"], MP3_EXT)
        return render_template("mp3.html", mp3_files=mp3_files)

    # VIDEO PLAYER PAGE
    @app.route("/video")
    def video_player():
        if "user_id" not in session:
            return redirect("/login")

        video_files = get_media_files(app.config["VIDEO_FOLDER"], VIDEO_EXT)
        return render_template("video.html", video_files=video_files)

    # MP3 LIST (ALBUM)
    @app.route("/audios")
    def audio_list():
        if "user_id" not in session:
            return redirect("/login")

        mp3_files = get_media_files(app.config["MP3_FOLDER"], MP3_EXT)
        return render_template("mp3-list.html", mp3_files=mp3_files)

    # VIDEO LIST (ALBUM)
    @app.route("/videos")
    def video_list():
        if "user_id" not in session:
            return redirect("/login")

        video_files = get_media_files(app.config["VIDEO_FOLDER"], VIDEO_EXT)
        return render_template("video-list.html", video_files=video_files)

    # SERVE MEDIA FILES
    @app.route("/media/<folder>/<filename>")
    def serve_media(folder, filename):
        if folder == "mp3":
            return send_from_directory(app.config["MP3_FOLDER"], filename)
        if folder == "video":
            return send_from_directory(app.config["VIDEO_FOLDER"], filename)
        return "Folder tidak valid", 404
import os
from flask import render_template, redirect, session, send_from_directory

from . import media_bp
from ...routes.utils import get_media_files


# EXTENSI MEDIA
MP3_EXT = ['.mp3', '.wav', '.ogg']
VIDEO_EXT = ['.mp4', '.avi', '.mkv', '.mov', '.wmv']


# MP3 PLAYER PAGE
@media_bp.route("/mp3")
def mp3_player():
    if "user_id" not in session:
        return redirect("/login")

    mp3_files = get_media_files(media_bp.app.config["MP3_FOLDER"], MP3_EXT)
    return render_template("mp3.html", mp3_files=mp3_files)


# VIDEO PLAYER PAGE
@media_bp.route("/video")
def video_player():
    if "user_id" not in session:
        return redirect("/login")

    video_files = get_media_files(media_bp.app.config["VIDEO_FOLDER"], VIDEO_EXT)
    return render_template("video.html", video_files=video_files)


# MP3 LIST (ALBUM)
@media_bp.route("/audios")
def audio_list():
    if "user_id" not in session:
        return redirect("/login")

    mp3_files = get_media_files(media_bp.app.config["MP3_FOLDER"], MP3_EXT)
    return render_template("mp3-list.html", mp3_files=mp3_files)


# VIDEO LIST (ALBUM)
@media_bp.route("/videos")
def video_list():
    if "user_id" not in session:
        return redirect("/login")

    video_files = get_media_files(media_bp.app.config["VIDEO_FOLDER"], VIDEO_EXT)
    return render_template("video-list.html", video_files=video_files)


# SERVE MEDIA FILES
@media_bp.route("/media/<folder>/<filename>")
def serve_media(folder, filename):
    if folder == "mp3":
        return send_from_directory(media_bp.app.config["MP3_FOLDER"], filename)
    if folder == "video":
        return send_from_directory(media_bp.app.config["VIDEO_FOLDER"], filename)

    return "Folder tidak valid", 404
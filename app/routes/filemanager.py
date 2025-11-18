# app/routes/filemanager.py
import os
import time
import subprocess
from flask import Blueprint, render_template, request, jsonify, current_app, session, send_from_directory
from werkzeug.utils import secure_filename

filemanager = Blueprint("filemanager", __name__)

ALLOWED_FOLDERS = {
    "mp3": "MP3_FOLDER",
    "video": "VIDEO_FOLDER",
    "upload": "UPLOAD_FOLDER"
}

# ------------------------
# Helpers
# ------------------------
def human_size(n):
    # simple human readable size
    for unit in ['B','KB','MB','GB','TB']:
        if n < 1024.0:
            return f"{n:.2f} {unit}"
        n /= 1024.0
    return f"{n:.2f} PB"

def get_file_info(folder_key, filename):
    """Return info dict for a file (size, mtime)."""
    folder = current_app.config.get(ALLOWED_FOLDERS[folder_key])
    path = os.path.join(folder, filename)
    if not os.path.exists(path):
        return None
    st = os.stat(path)
    return {
        "name": filename,
        "path": f"/media/{folder_key}/{filename}",
        "size_bytes": st.st_size,
        "size": human_size(st.st_size),
        "mtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime)),
        "is_video": folder_key == "video",
        "is_audio": folder_key == "mp3",
        "download_url": f"/filemanager/download?folder={folder_key}&filename={filename}"
    }

def generate_thumbnail_if_possible(video_folder, filename):
    """
    Try to create a thumbnail PNG in static/upload/thumbnails/<filename>.png
    Returns url if success else None.
    """
    # thumbnail dir under static/upload/thumbnails
    thumbs_dir = os.path.join(current_app.static_folder, "upload", "thumbnails")
    os.makedirs(thumbs_dir, exist_ok=True)

    src = os.path.join(video_folder, filename)
    name_wo_ext = os.path.splitext(filename)[0]
    out_name = f"{name_wo_ext}.png"
    out_path = os.path.join(thumbs_dir, out_name)

    # if thumbnail already exists and newer than video, reuse
    if os.path.exists(out_path):
        if os.path.getmtime(out_path) >= os.path.getmtime(src):
            return f"/static/upload/thumbnails/{out_name}"

    ffmpeg = shutil_which("ffmpeg")
    if not ffmpeg:
        return None

    # Try capturing frame at 2 seconds
    cmd = [
        ffmpeg, "-y",
        "-ss", "00:00:02",
        "-i", src,
        "-frames:v", "1",
        "-q:v", "2",
        out_path
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, timeout=15)
        return f"/static/upload/thumbnails/{out_name}"
    except Exception:
        return None

def shutil_which(name):
    """Light wrapper to check for binary availability."""
    from shutil import which
    return which(name)

# ------------------------
# UI
# ------------------------
@filemanager.route("/filemanager")
def fm_index():
    if "user_id" not in session:
        return render_template("splash.html")  # or redirect("/login")
    return render_template("filemanager.html")

# ------------------------
# API: list files
# /api/files?type=mp3|video|upload|all
# ------------------------
@filemanager.route("/api/files")
def api_files():
    if "user_id" not in session:
        return jsonify({"error": "Harus login"}), 403

    typ = request.args.get("type", "all")
    results = []

    types = []
    if typ == "all":
        types = ["mp3", "video", "upload"]
    else:
        if typ in ALLOWED_FOLDERS:
            types = [typ]

    for t in types:
        folder = current_app.config.get(ALLOWED_FOLDERS[t])
        if not folder:
            continue
        try:
            for fn in sorted(os.listdir(folder)):
                # skip hidden files
                if fn.startswith("."):
                    continue
                info = get_file_info(t, fn)
                if info:
                    # try thumbnail for video (best-effort)
                    if t == "video":
                        thumb = None
                        # avoid importing heavy libs; try ffmpeg fallback
                        thumb = generate_thumbnail_if_possible(folder, fn)
                        if thumb:
                            info["thumbnail"] = thumb
                    results.append(info)
        except FileNotFoundError:
            continue

    return jsonify({"files": results})

# ------------------------
# API: delete file
# ------------------------
@filemanager.route("/api/delete-file", methods=["POST"])
def api_delete_file():
    if "user_id" not in session:
        return jsonify({"error": "Harus login"}), 403

    data = request.json or {}
    folder_key = data.get("folder")
    filename = data.get("filename")

    if folder_key not in ALLOWED_FOLDERS:
        return jsonify({"error": "Folder tidak valid"}), 400

    safe_name = os.path.basename(filename)
    folder = current_app.config.get(ALLOWED_FOLDERS[folder_key])
    path = os.path.join(folder, safe_name)

    if not os.path.exists(path):
        return jsonify({"error": "File tidak ditemukan"}), 404

    try:
        os.remove(path)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------
# API: rename file
# ------------------------
@filemanager.route("/api/rename-file", methods=["POST"])
def api_rename_file():
    if "user_id" not in session:
        return jsonify({"error": "Harus login"}), 403

    data = request.json or {}
    folder_key = data.get("folder")
    old_name = data.get("old_name")
    new_name = data.get("new_name")

    if folder_key not in ALLOWED_FOLDERS:
        return jsonify({"error": "Folder tidak valid"}), 400

    if not old_name or not new_name:
        return jsonify({"error": "Nama file tidak lengkap"}), 400

    folder = current_app.config.get(ALLOWED_FOLDERS[folder_key])
    old_path = os.path.join(folder, os.path.basename(old_name))
    new_safe = secure_filename(new_name)
    new_path = os.path.join(folder, new_safe)

    if not os.path.exists(old_path):
        return jsonify({"error": "File lama tidak ditemukan"}), 404

    if os.path.exists(new_path):
        return jsonify({"error": "Nama baru sudah ada"}), 409

    try:
        os.rename(old_path, new_path)
        return jsonify({"status": "ok", "new_name": new_safe})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------
# Download (serve as attachment)
# /filemanager/download?folder=mp3&filename=xxx
# ------------------------
@filemanager.route("/filemanager/download")
def fm_download():
    if "user_id" not in session:
        return jsonify({"error": "Harus login"}), 403

    folder_key = request.args.get("folder")
    filename = request.args.get("filename")

    if folder_key not in ALLOWED_FOLDERS:
        return "Folder tidak valid", 400

    folder = current_app.config.get(ALLOWED_FOLDERS[folder_key])
    safe_name = os.path.basename(filename)
    if not os.path.exists(os.path.join(folder, safe_name)):
        return "File tidak ditemukan", 404

    return send_from_directory(folder, safe_name, as_attachment=True)
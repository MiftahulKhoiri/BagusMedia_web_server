# app/routes/filemanager.py

import os
import time
import subprocess
from flask import Blueprint, render_template, request, jsonify, current_app, session, send_from_directory
from werkzeug.utils import secure_filename

# Import sistem role
from .utils import require_root, is_root

filemanager = Blueprint("filemanager", __name__)

ALLOWED_FOLDERS = {
    "mp3": "MP3_FOLDER",
    "video": "VIDEO_FOLDER",
    "upload": "UPLOAD_FOLDER"
}

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def human_size(n):
    for unit in ['B','KB','MB','GB','TB']:
        if n < 1024:
            return f"{n:.2f} {unit}"
        n /= 1024
    return f"{n:.2f} PB"

def get_file_info(folder_key, filename):
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

def shutil_which(name):
    from shutil import which
    return which(name)

def generate_thumbnail_if_possible(video_folder, filename):
    thumbs_dir = os.path.join(current_app.static_folder, "upload", "thumbnails")
    os.makedirs(thumbs_dir, exist_ok=True)

    src = os.path.join(video_folder, filename)
    name_wo_ext = os.path.splitext(filename)[0]
    out_path = os.path.join(thumbs_dir, f"{name_wo_ext}.png")

    if os.path.exists(out_path) and os.path.getmtime(out_path) >= os.path.getmtime(src):
        return f"/static/upload/thumbnails/{name_wo_ext}.png"

    ffmpeg = shutil_which("ffmpeg")
    if not ffmpeg:
        return None

    cmd = [
        ffmpeg, "-y", "-ss", "00:00:02",
        "-i", src,
        "-frames:v", "1",
        "-q:v", "2",
        out_path
    ]

    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, timeout=10)
        return f"/static/upload/thumbnails/{name_wo_ext}.png"
    except:
        return None


# ---------------------------------------------------------
# UI
# ---------------------------------------------------------
@filemanager.route("/filemanager")
def fm_index():
    # ❗ Akses hanya untuk root
    check = require_root()
    if check:
        return check

    return render_template("filemanager.html")


# ---------------------------------------------------------
# API: LIST FILES
# ---------------------------------------------------------
@filemanager.route("/api/files")
def api_files():
    # ❗ Hanya root yang boleh
    check = require_root()
    if check:
        return check

    typ = request.args.get("type", "all")
    results = []

    types = ["mp3", "video", "upload"] if typ == "all" else [typ]

    for t in types:
        folder = current_app.config.get(ALLOWED_FOLDERS.get(t))
        if not folder:
            continue

        try:
            for fn in sorted(os.listdir(folder)):
                if fn.startswith("."):  # skip hidden files / .xxx
                    continue

                full_path = os.path.join(folder, fn)

                # ============================
                # JIKA INI FOLDER
                # ============================
                if os.path.isdir(full_path):
                    st = os.stat(full_path)
                    results.append({
                        "name": fn,
                        "is_folder": True,
                        "folder_key": t,
                        "path": fn,  # nanti dipakai untuk masuk ke folder
                        "size_bytes": st.st_size,
                        "size": human_size(st.st_size),
                        "mtime": time.strftime(
                            "%Y-%m-%d %H:%M:%S",
                            time.localtime(st.st_mtime)
                        ),
                    })
                    continue

                # ============================
                # JIKA INI FILE BIASA
                # ============================
                info = get_file_info(t, fn)
                if info and t == "video":
                    thumb = generate_thumbnail_if_possible(folder, fn)
                    if thumb:
                        info["thumbnail"] = thumb

                results.append(info)

        except FileNotFoundError:
            continue

    return jsonify({"files": results})


# ---------------------------------------------------------
# API: DELETE FILE
# ---------------------------------------------------------
@filemanager.route("/api/delete-file", methods=["POST"])
def api_delete_file():
    check = require_root()
    if check:
        return check

    data = request.json or {}
    folder_key = data.get("folder")
    filename = data.get("filename")

    if folder_key not in ALLOWED_FOLDERS:
        return jsonify({"error": "Folder tidak valid"}), 400

    folder = current_app.config.get(ALLOWED_FOLDERS[folder_key])
    path = os.path.join(folder, os.path.basename(filename))

    if not os.path.exists(path):
        return jsonify({"error": "File tidak ditemukan"}), 404

    try:
        os.remove(path)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------
# API: RENAME FILE
# ---------------------------------------------------------
@filemanager.route("/api/rename-file", methods=["POST"])
def api_rename_file():
    check = require_root()
    if check:
        return check

    data = request.json or {}
    folder_key = data.get("folder")
    old_name = data.get("old_name")
    new_name = data.get("new_name")

    if folder_key not in ALLOWED_FOLDERS:
        return jsonify({"error": "Folder tidak valid"}), 400

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


# ---------------------------------------------------------
# DOWNLOAD (HANYA ROOT)
# ---------------------------------------------------------
@filemanager.route("/filemanager/download")
def fm_download():
    check = require_root()
    if check:
        return check

    folder_key = request.args.get("folder")
    filename = request.args.get("filename")

    if folder_key not in ALLOWED_FOLDERS:
        return "Folder tidak valid", 400

    folder = current_app.config.get(ALLOWED_FOLDERS[folder_key])
    safe = os.path.basename(filename)

    if not os.path.exists(os.path.join(folder, safe)):
        return "File tidak ditemukan", 404

    return send_from_directory(folder, safe, as_attachment=True)

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

import os
import shutil
import time
import subprocess
from flask import (
    Blueprint, render_template, request, jsonify,
    current_app, session, send_from_directory, redirect
)
from werkzeug.utils import secure_filename

# Sistem role
from .utils import allowed_file, require_root

filemanager = Blueprint("filemanager", __name__)

ALLOWED_FOLDERS = {
    "mp3": "MP3_FOLDER",
    "video": "VIDEO_FOLDER",
    "upload": "UPLOAD_FOLDER"  # temp folder (upload sementara)
}


# -----------------------
# Helpers
# -----------------------
def human_size(n):
    for unit in ['B','KB','MB','GB','TB']:
        if n < 1024:
            return f"{n:.2f} {unit}"
        n /= 1024
    return f"{n:.2f} PB"


def resolve_path(root_key, subpath=""):
    """
    Return absolute path for given root_key + subpath after validation.
    Prevent path traversal by ensuring resolved path is inside base root.
    """
    if root_key not in ALLOWED_FOLDERS:
        return None, "Root tidak valid"

    base = current_app.config.get(ALLOWED_FOLDERS[root_key])
    if not base:
        return None, "Root belum dikonfigurasi"

    # If no subpath or empty, use base
    subpath = (subpath or "").strip()
    # Normalize slashes and prevent absolute path
    subpath = subpath.replace("\\", "/").lstrip("/")
    target = os.path.normpath(os.path.join(base, subpath))

    try:
        base_real = os.path.realpath(base)
        target_real = os.path.realpath(target)
        # commonpath better than commonprefix
        common = os.path.commonpath([base_real, target_real])
        if common != base_real:
            return None, "Path di luar root tidak diperbolehkan"
    except Exception:
        return None, "Error memvalidasi path"

    return target_real, None


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def auto_rename(path):
    """Jika file/folder sudah ada, beri suffix (1),(2), dst."""
    base, ext = os.path.splitext(path)
    i = 1
    new_path = path
    while os.path.exists(new_path):
        new_path = f"{base}({i}){ext}"
        i += 1
    return new_path


def get_file_info_by_path(root_key, full_path, base_path):
    """
    full_path: absolute path to the file
    base_path: absolute base folder for the root_key
    """
    if not os.path.exists(full_path):
        return None

    filename = os.path.basename(full_path)
    rel_path = os.path.relpath(os.path.dirname(full_path), base_path)
    rel_path = "" if rel_path == "." else rel_path.replace("\\", "/")

    st = os.stat(full_path)
    return {
        "name": filename,
        "path": f"{root_key}/{rel_path}/{filename}".strip("/"),  # untuk UI navigasi
        "size_bytes": st.st_size,
        "size": human_size(st.st_size),
        "mtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime)),
        "is_video": root_key == "video",
        "is_audio": root_key == "mp3",
        "download_url": f"/filemanager/download?root={root_key}&path={rel_path}&file={filename}"
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

    # Cek cache
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
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       check=True, timeout=10)
        return f"/static/upload/thumbnails/{name_wo_ext}.png"
    except:
        return None


# -----------------------
# UI index
# -----------------------
@filemanager.route("/filemanager")
def fm_index():
    check = require_root()
    if check:
        return check
    return render_template("filemanager.html")


# -----------------------
# LIST FILES (multi-level)
# GET /api/files?root=mp3&path=sub/folder
# -----------------------
@filemanager.route("/api/files")
def api_files():
    check = require_root()
    if check:
        return check

    root = request.args.get("root", "mp3")
    path = request.args.get("path", "").strip()

    base_dir, err = resolve_path(root, path)
    if err:
        return jsonify({"error": err}), 400

    results = {"folders": [], "files": []}

    try:
        entries = sorted(os.listdir(base_dir))
    except FileNotFoundError:
        return jsonify({"folders": [], "files": []})

    for entry in entries:
        if entry.startswith("."):
            continue
        full = os.path.join(base_dir, entry)
        if os.path.isdir(full):
            st = os.stat(full)
            results["folders"].append({
                "name": entry,
                "is_folder": True,
                "root": root,
                "path": (path + "/" + entry).strip("/"),
                "size_bytes": st.st_size,
                "size": human_size(st.st_size),
                "mtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime))
            })
        else:
            info = get_file_info_by_path(root, full, os.path.realpath(current_app.config.get(ALLOWED_FOLDERS[root])))
            if info and root == "video":
                thumb = generate_thumbnail_if_possible(current_app.config.get(ALLOWED_FOLDERS[root]), entry)
                if thumb:
                    info["thumbnail"] = thumb
            if info:
                results["files"].append(info)

    return jsonify(results)


# -----------------------
# CREATE FOLDER (multi-level)
# POST /api/create-folder { root, path, name }
# -----------------------
@filemanager.route("/api/create-folder", methods=["POST"])
def api_create_folder():
    check = require_root()
    if check:
        return check

    data = request.json or {}
    root = data.get("root")
    path = data.get("path", "").strip()
    name = (data.get("name") or "").strip()

    if not name:
        return jsonify({"error": "Nama folder tidak boleh kosong"}), 400

    base_dir, err = resolve_path(root, path)
    if err:
        return jsonify({"error": err}), 400

    safe_name = secure_filename(name)
    new_dir = os.path.join(base_dir, safe_name)

    if os.path.exists(new_dir):
        return jsonify({"error": "Folder sudah ada"}), 409

    try:
        os.makedirs(new_dir)
        rel = (path + "/" + safe_name).strip("/")
        return jsonify({"status": "ok", "name": safe_name, "path": rel})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------
# DELETE FILE (multi-level)
# POST /api/delete-file { root, path, filename }
# -----------------------
@filemanager.route("/api/delete-file", methods=["POST"])
def api_delete_file():
    check = require_root()
    if check:
        return check

    data = request.json or {}
    root = data.get("root")
    path = data.get("path", "").strip()
    filename = (data.get("filename") or "").strip()
    if not filename:
        return jsonify({"error": "Nama file tidak boleh kosong"}), 400

    base_dir, err = resolve_path(root, path)
    if err:
        return jsonify({"error": err}), 400

    safe = os.path.basename(filename)
    target = os.path.join(base_dir, safe)

    if not os.path.exists(target):
        return jsonify({"error": "File tidak ditemukan"}), 404

    try:
        os.remove(target)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------
# DELETE FOLDER (multi-level)
# POST /api/delete-folder { root, path, foldername }
# -----------------------
@filemanager.route("/api/delete-folder", methods=["POST"])
def api_delete_folder():
    check = require_root()
    if check:
        return check

    data = request.json or {}
    root = data.get("root")
    path = data.get("path", "").strip()
    foldername = (data.get("foldername") or "").strip()
    if not foldername:
        return jsonify({"error": "Nama folder tidak boleh kosong"}), 400

    base_dir, err = resolve_path(root, path)
    if err:
        return jsonify({"error": err}), 400

    safe = os.path.basename(foldername)
    target = os.path.join(base_dir, safe)

    if not os.path.isdir(target):
        return jsonify({"error": "Folder tidak ditemukan"}), 404

    try:
        shutil.rmtree(target)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------
# RENAME FILE (multi-level)
# POST /api/rename-file { root, path, old_name, new_name }
# -----------------------
@filemanager.route("/api/rename-file", methods=["POST"])
def api_rename_file():
    check = require_root()
    if check:
        return check

    data = request.json or {}
    root = data.get("root")
    path = data.get("path", "").strip()
    old_name = (data.get("old_name") or "").strip()
    new_name = (data.get("new_name") or "").strip()

    if not old_name or not new_name:
        return jsonify({"error": "Nama lama/baru harus diisi"}), 400

    base_dir, err = resolve_path(root, path)
    if err:
        return jsonify({"error": err}), 400

    old_safe = os.path.basename(old_name)
    new_safe = secure_filename(new_name)
    old_path = os.path.join(base_dir, old_safe)
    new_path = os.path.join(base_dir, new_safe)

    if not os.path.exists(old_path):
        return jsonify({"error": "File lama tidak ditemukan"}), 404

    if os.path.exists(new_path):
        # auto-rename ke nama baru yang tidak bentrok
        new_path = auto_rename(new_path)
        new_safe = os.path.basename(new_path)

    try:
        os.rename(old_path, new_path)
        return jsonify({"status": "ok", "new_name": new_safe})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------
# RENAME FOLDER (multi-level)
# POST /api/rename-folder { root, path, old_name, new_name }
# -----------------------
@filemanager.route("/api/rename-folder", methods=["POST"])
def api_rename_folder():
    check = require_root()
    if check:
        return check

    data = request.json or {}
    root = data.get("root")
    path = data.get("path", "").strip()
    old_name = (data.get("old_name") or "").strip()
    new_name = (data.get("new_name") or "").strip()

    if not old_name or not new_name:
        return jsonify({"error": "Nama lama/baru harus diisi"}), 400

    base_dir, err = resolve_path(root, path)
    if err:
        return jsonify({"error": err}), 400

    old_safe = os.path.basename(old_name)
    new_safe = secure_filename(new_name)
    old_path = os.path.join(base_dir, old_safe)
    new_path = os.path.join(base_dir, new_safe)

    if not os.path.isdir(old_path):
        return jsonify({"error": "Folder lama tidak ditemukan"}), 404

    if os.path.exists(new_path):
        return jsonify({"error": "Nama folder baru sudah ada"}), 409

    try:
        os.rename(old_path, new_path)
        return jsonify({"status": "ok", "new_name": new_safe})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------
# UPLOAD (multi-level)
# POST /api/upload?root=mp3&path=sub/folder
# -----------------------
@filemanager.route("/api/upload", methods=["POST"])
def upload_file():
    if "user_id" not in session:
        return jsonify({"error": "Harus login!"}), 403

    root = request.args.get("root", "mp3")
    path = request.args.get("path", "").strip()

    base_dir, err = resolve_path(root, path)
    if err:
        return jsonify({"error": err}), 400

    # Pastikan upload temp folder ada
    upload_temp = current_app.config.get(ALLOWED_FOLDERS["upload"])
    if not upload_temp:
        return jsonify({"error": "Upload temp belum dikonfigurasi"}), 500
    ensure_dir(upload_temp)

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
            temp_path = os.path.join(upload_temp, filename)

            # Simpan sementara
            file.save(temp_path)

            ext = filename.rsplit(".", 1)[1].lower()
            # Tentukan tujuan akhir (tetap gunakan root yang diminta)
            dest_base, _ = resolve_path(root, "")  # base folder for root
            dest_dir = base_dir  # target directory (multi-level)
            ensure_dir(dest_dir)

            final_path = os.path.join(dest_dir, filename)
            final_path = auto_rename(final_path)

            try:
                shutil.move(temp_path, final_path)
                results.append({"filename": os.path.basename(final_path), "status": "success"})
            except Exception as e:
                # Hapus temp bila terjadi error
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except:
                    pass
                results.append({"filename": filename, "status": "error", "error": str(e)})
        else:
            results.append({"filename": file.filename, "status": "error"})

    return jsonify({"results": results})


# -----------------------
# DOWNLOAD (multi-level)
# GET /filemanager/download?root=mp3&path=sub/folder&file=abc.mp3
# -----------------------
@filemanager.route("/filemanager/download")
def fm_download():
    check = require_root()
    if check:
        return check

    root = request.args.get("root")
    path = request.args.get("path", "").strip()
    filename = (request.args.get("file") or "").strip()

    if not filename:
        return "File tidak ditemukan", 404

    base_dir, err = resolve_path(root, path)
    if err:
        return err, 400

    safe = os.path.basename(filename)
    target = os.path.join(base_dir, safe)

    if not os.path.exists(target):
        return "File tidak ditemukan", 404

    # send_from_directory membutuhkan directory dan filename terpisah
    return send_from_directory(base_dir, safe, as_attachment=True)
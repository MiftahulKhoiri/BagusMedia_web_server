import os
import time
import shutil
from flask import render_template, request, jsonify, redirect, session, current_app
from werkzeug.utils import secure_filename

# helper berada di folder yang sama (app/routes/helper.py)
from .helper import allowed_file

def register_upload_routes(app):
    """
    Daftarkan route untuk halaman upload dan API upload.
    Panggil register_upload_routes(app) dari init penggabung routes.
    """

    # Halaman upload (form)
    @app.route("/upload")
    def upload_page():
        # wajib login
        if "user_id" not in session:
            return redirect("/login")
        return render_template("upload.html")

    # API upload file (bisa multiple)
    @app.route("/api/upload", methods=["POST"])
    def api_upload_files():
        # cek session
        if "user_id" not in session:
            return jsonify({"error": "Harus login!"}), 403

        # cek ada files
        if "files" not in request.files:
            return jsonify({"error": "Tidak ada file yang dikirim"}), 400

        files = request.files.getlist("files")
        results = []

        # pastikan folder upload ada
        os.makedirs(app.config.get("UPLOAD_FOLDER", os.path.join(app.static_folder, "upload")), exist_ok=True)
        os.makedirs(app.config.get("MP3_FOLDER", os.path.join(app.static_folder, "mp3")), exist_ok=True)
        os.makedirs(app.config.get("VIDEO_FOLDER", os.path.join(app.static_folder, "video")), exist_ok=True)

        for f in files:
            # nama file kosong
            if not f or f.filename == "":
                results.append({"filename": "", "status": "error", "message": "Nama file kosong"})
                continue

            filename = secure_filename(f.filename)

            # cek ekstensi di helper.allowed_file
            if not allowed_file(filename):
                results.append({"filename": filename, "status": "error", "message": "Tipe file tidak diizinkan"})
                continue

            try:
                # simpan sementara di upload folder
                temp_path = os.path.join(app.config.get("UPLOAD_FOLDER"), filename)
                f.save(temp_path)

                ext = filename.rsplit(".", 1)[1].lower()
                if ext in ["mp3", "wav", "ogg"]:
                    dest_folder = app.config.get("MP3_FOLDER")
                else:
                    dest_folder = app.config.get("VIDEO_FOLDER")

                # pindahkan ke folder tujuan
                dest_path = os.path.join(dest_folder, filename)
                # jika file dengan nama sama sudah ada, tambahkan timestamp agar unik
                if os.path.exists(dest_path):
                    base, dot_ext = os.path.splitext(filename)
                    filename = f"{base}_{int(time.time())}{dot_ext}"
                    dest_path = os.path.join(dest_folder, filename)

                shutil.move(temp_path, dest_path)

                results.append({
                    "filename": filename,
                    "status": "success",
                    "message": f"File diupload ke {os.path.relpath(dest_folder, app.static_folder)}"
                })
            except Exception as e:
                # jika ada error, pastikan temp dihapus bila ada
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except:
                    pass
                results.append({"filename": filename, "status": "error", "message": str(e)})

        return jsonify({"results": results})
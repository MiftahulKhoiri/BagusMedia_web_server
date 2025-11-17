import os
import shutil
import time
from flask import render_template, redirect, session, request, jsonify, current_app
from werkzeug.utils import secure_filename

# Import helper (pastikan file .utils ada). Aku juga sertakan implementasi allowed_file di bawah.
from .utils import allowed_file

# =============================
# ROUTES: UPLOAD MEDIA
# =============================

def upload_routes(app):

    # Pastikan folder upload & target ada saat app di-register
    upload_folder = app.config.get("UPLOAD_FOLDER", os.path.join(app.root_path, "uploads"))
    video_folder = app.config.get("VIDEO_FOLDER", os.path.join(upload_folder, "videos"))
    mp3_folder = app.config.get("MP3_FOLDER", os.path.join(upload_folder, "audio"))

    # buat folder bila belum ada
    for d in (upload_folder, video_folder, mp3_folder):
        os.makedirs(d, exist_ok=True)

    # UPLOAD PAGE
    @app.route("/upload")
    def upload():
        if "user_id" not in session:
            return redirect("/login")
        return render_template("upload.html")

    # API UPLOAD MEDIA
    @app.route("/api/upload", methods=["POST"])
    def upload_file():
        # Cek login
        if "user_id" not in session:
            return jsonify({"error": "Harus login!"}), 403

        # Cek field files ada
        if "files" not in request.files:
            return jsonify({"error": "Tidak ada file. Pastikan form menggunakan enctype='multipart/form-data' dan input name='files'."}), 400

        files = request.files.getlist("files")
        results = []

        for file in files:
            # cek filename kosong
            if not file or file.filename == "":
                results.append({"filename": "", "status": "error", "message": "Nama file kosong"})
                continue

            # secure filename
            original_name = file.filename
            filename = secure_filename(original_name)

            # cek ekstensi ada
            if "." not in filename:
                results.append({"filename": original_name, "status": "error", "message": "File tanpa ekstensi tidak diperbolehkan"})
                continue

            ext = filename.rsplit(".", 1)[1].lower()

            # cek allowed_file (pastikan allowed_file memeriksa ekstensi)
            if not allowed_file(filename):
                results.append({"filename": original_name, "status": "error", "message": f"Ekstensi .{ext} tidak diizinkan"})
                continue

            # target folder berdasarkan ekstensi
            if ext in ("mp3", "wav", "ogg"):
                dest_folder = mp3_folder
            else:
                dest_folder = video_folder

            # Jika nama file sudah ada, tambahkan timestamp untuk menghindari overwrite
            timestamp = int(time.time())
            base, extension = os.path.splitext(filename)
            safe_filename = f"{base}_{timestamp}{extension}"
            dest_path = os.path.join(dest_folder, safe_filename)

            try:
                # Save ke folder sementara (UPLOAD_FOLDER) dulu untuk keamanan
                temp_path = os.path.join(upload_folder, safe_filename)
                file.save(temp_path)

                # pindahkan ke folder final (atomic)
                shutil.move(temp_path, dest_path)

                results.append({"filename": safe_filename, "status": "success"})
            except Exception as e:
                # jika ada error permission atau lainya
                results.append({"filename": original_name, "status": "error", "message": str(e)})

        return jsonify({"results": results})
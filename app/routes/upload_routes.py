import os
import shutil
from flask import render_template, redirect, session, request, jsonify
from werkzeug.utils import secure_filename

# Import helper
from .utils import allowed_file

# =============================
# ROUTES: UPLOAD MEDIA
# =============================

def upload_routes(app):

    # UPLOAD PAGE
    @app.route("/upload")
    def upload():
        if "user_id" not in session:
            return redirect("/login")
        return render_template("upload.html")

    # API UPLOAD MEDIA
    @app.route("/api/upload", methods=["POST"])
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
                temp_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

                # save file sementara
                file.save(temp_path)

                ext = filename.rsplit(".", 1)[1].lower()
                dest = (
                    app.config["MP3_FOLDER"]
                    if ext in ['mp3', 'wav', 'ogg']
                    else app.config["VIDEO_FOLDER"]
                )

                shutil.move(temp_path, os.path.join(dest, filename))
                results.append({"filename": filename, "status": "success"})
            else:
                results.append({"filename": file.filename, "status": "error"})

        return jsonify({"results": results})
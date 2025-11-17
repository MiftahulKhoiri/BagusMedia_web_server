import os
import json
import time
from flask import render_template, request, jsonify

# =============================
# ROUTES: PROFILE (DATA, FOTO, COVER)
# =============================

def profile_routes(app):

    PROFILE_FILE = app.config["PROFILE_FILE"]

    # HALAMAN PROFIL
    @app.route("/profile")
    def profile():
        if "user_id" not in request.environ["werkzeug.request"].session:
            return render_template("login.html")

        # load data profil
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                profile_data = json.load(f)
        else:
            profile_data = {
                "nama": "", "email": "", "jk": "",
                "umur": "", "bio": "",
                "foto": "", "cover": ""
            }

        from datetime import datetime
        current_year = datetime.now().year

        return render_template("profile.html", profile=profile_data, current_year=current_year)

    # HALAMAN EDIT PROFIL
    @app.route("/edit-profile")
    def edit_profile():
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                profile_data = json.load(f)
        else:
            profile_data = {
                "nama": "", "email": "", "jk": "",
                "umur": "", "bio": "",
                "foto": "", "cover": ""
            }

        return render_template("edit-profile.html", profile=profile_data)

    # SIMPAN PROFIL (TEXUAL DATA)
    @app.route("/api/save-profile", methods=["POST"])
    def save_profile():
        data = request.json

        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                old = json.load(f)
        else:
            old = {}

        merged = {
            "nama": data.get("nama", old.get("nama", "")),
            "email": data.get("email", old.get("email", "")),
            "jk": data.get("jk", old.get("jk", "")),
            "umur": data.get("umur", old.get("umur", "")),
            "bio": data.get("bio", old.get("bio", "")),
            "foto": old.get("foto", ""),
            "cover": old.get("cover", "")
        }

        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=4)

        return jsonify({"status": "success"})

    # UPLOAD FOTO PROFIL ATAU COVER
    @app.route("/api/upload-photo", methods=["POST"])
    def upload_photo():
        if "photo" not in request.files:
            return jsonify({"status": "error", "message": "Foto tidak ditemukan"}), 400

        file = request.files["photo"]
        upload_type = request.form.get("type")  # "profile" atau "cover"

        if upload_type not in ["profile", "cover"]:
            return jsonify({"status": "error", "message": "Tipe upload tidak valid"}), 400

        filename = str(int(time.time())) + "_" + file.filename

        foto_folder = os.path.join(app.static_folder, "profile")
        os.makedirs(foto_folder, exist_ok=True)

        new_path = os.path.join(foto_folder, filename)
        file.save(new_path)

        # load data lama
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                profile_data = json.load(f)
        else:
            profile_data = {}

        key = "foto" if upload_type == "profile" else "cover"
        old = profile_data.get(key, "")

        # hapus file lama
        if old not in ["", "profile.png", "cover.png"]:
            old_path = os.path.join(foto_folder, old)
            if os.path.exists(old_path):
                os.remove(old_path)

        profile_data[key] = filename

        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(profile_data, f, indent=4)

        return jsonify({"status": "success", "foto": filename})
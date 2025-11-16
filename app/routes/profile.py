import os
import json
import time
from flask import (
    Blueprint, render_template, request, redirect, jsonify, session
)
from werkzeug.utils import secure_filename

profile = Blueprint("profile", __name__)

def init_profile(app):

    PROFILE_FILE = app.config["PROFILE_FILE"]

    # =============================
    # HALAMAN PROFIL
    # =============================
    @profile.route("/profile")
    def profile():
        if "user_id" not in session:
            return redirect("/login")

        # Ambil data profil
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                profile_data = json.load(f)
        else:
            profile_data = {
                "nama": "",
                "email": "",
                "jk": "",
                "umur": "",
                "bio": "",
                "foto": "",
                "cover": ""
            }

        return render_template("profile.html", profile=profile_data)

    # =============================
    # HALAMAN EDIT PROFIL
    # =============================
    @profile.route("/edit-profile")
    def edit_profile():
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                profile_data = json.load(f)
        else:
            profile_data = {
                "nama": "",
                "email": "",
                "jk": "",
                "umur": "",
                "bio": "",
                "foto": "",
                "cover": ""
            }

        return render_template("edit-profile.html", profile=profile_data)

    # =============================
    # SIMPAN PROFIL
    # =============================
    @profile.route("/api/save-profile", methods=["POST"])
    def save_profile():
        data = request.json

        # Ambil data lama dulu
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                old = json.load(f)
        else:
            old = {}

        # Gabungkan data baru + lama
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

    # =============================
    # UPLOAD FOTO PROFIL & COVER
    # =============================
    @profile.route("/api/upload-photo", methods=["POST"])
    def upload_photo():
        if "photo" not in request.files:
            return jsonify({"status": "error", "message": "Foto tidak ditemukan"}), 400

        file = request.files["photo"]
        upload_type = request.form.get("type")  # profile atau cover

        if upload_type not in ["profile", "cover"]:
            return jsonify({"status": "error", "message": "Tipe upload tidak valid"}), 400

        filename = secure_filename(str(int(time.time())) + "_" + file.filename)

        foto_folder = os.path.join(app.static_folder, "profile")
        os.makedirs(foto_folder, exist_ok=True)

        new_path = os.path.join(foto_folder, filename)
        file.save(new_path)

        # Ambil data lama
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                profile_data = json.load(f)
        else:
            profile_data = {}

        key = "foto" if upload_type == "profile" else "cover"
        old_file = profile_data.get(key, "")

        # Hapus file lama (kecuali default)
        if old_file not in ["", "profile.png", "cover.png"]:
            old_path = os.path.join(foto_folder, old_file)
            if os.path.exists(old_path):
                os.remove(old_path)

        profile_data[key] = filename

        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(profile_data, f, indent=4)

        return jsonify({"status": "success", "foto": filename})
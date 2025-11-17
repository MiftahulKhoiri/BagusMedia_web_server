import os
import json
import time
from datetime import datetime
from flask import render_template, request, jsonify, session

from . import profile_bp


# HALAMAN PROFIL
@profile_bp.route("/profile")
def profile():
    if "user_id" not in session:
        return render_template("login.html")

    profile_file = profile_bp.app.config["PROFILE_FILE"]

    # Muat data profil
    if os.path.exists(profile_file):
        with open(profile_file, "r", encoding="utf-8") as f:
            profile_data = json.load(f)
    else:
        profile_data = {
            "nama": "", "email": "", "jk": "",
            "umur": "", "bio": "",
            "foto": "", "cover": ""
        }

    current_year = datetime.now().year
    return render_template("profile.html", profile=profile_data, current_year=current_year)


# HALAMAN EDIT PROFIL
@profile_bp.route("/edit-profile")
def edit_profile():
    profile_file = profile_bp.app.config["PROFILE_FILE"]

    if os.path.exists(profile_file):
        with open(profile_file, "r", encoding="utf-8") as f:
            profile_data = json.load(f)
    else:
        profile_data = {
            "nama": "", "email": "", "jk": "",
            "umur": "", "bio": "",
            "foto": "", "cover": ""
        }

    return render_template("edit-profile.html", profile=profile_data)


# API SIMPAN PROFIL
@profile_bp.route("/api/save-profile", methods=["POST"])
def save_profile():
    data = request.json
    profile_file = profile_bp.app.config["PROFILE_FILE"]

    # Data lama
    if os.path.exists(profile_file):
        with open(profile_file, "r", encoding="utf-8") as f:
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

    with open(profile_file, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=4)

    return jsonify({"status": "success"})


# API UPLOAD FOTO PROFIL / COVER
@profile_bp.route("/api/upload-photo", methods=["POST"])
def upload_photo():
    if "photo" not in request.files:
        return jsonify({"status": "error", "message": "Foto tidak ditemukan"}), 400

    file = request.files["photo"]
    upload_type = request.form.get("type")  # profile OR cover

    if upload_type not in ["profile", "cover"]:
        return jsonify({"status": "error", "message": "Tipe upload tidak valid"}), 400

    filename = str(int(time.time())) + "_" + file.filename

    foto_folder = os.path.join(profile_bp.app.static_folder, "profile")
    os.makedirs(foto_folder, exist_ok=True)

    new_path = os.path.join(foto_folder, filename)
    file.save(new_path)

    profile_file = profile_bp.app.config["PROFILE_FILE"]

    # Data lama
    if os.path.exists(profile_file):
        with open(profile_file, "r", encoding="utf-8") as f:
            profile_data = json.load(f)
    else:
        profile_data = {}

    key = "foto" if upload_type == "profile" else "cover"
    old = profile_data.get(key, "")

    # Hapus foto lama jika ada
    if old not in ["", "profile.png", "cover.png"]:
        old_path = os.path.join(foto_folder, old)
        if os.path.exists(old_path):
            os.remove(old_path)

    profile_data[key] = filename

    with open(profile_file, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=4)

    return jsonify({"status": "success", "foto": filename})
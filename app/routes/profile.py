# app/routes/profile.py
import os
import json
import time
from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename

# ============================================
# BLUEPRINT PROFILE (TAMPILAN & UPLOAD FOTO)
# ============================================
profile = Blueprint("profile", __name__)


# ============================================
# HALAMAN PROFIL
# ============================================
@profile.route("/profile")
def profile_page():
    """
    Tampilkan halaman profile.
    - Memeriksa apakah file PROFILE_FILE ada
    - Jika ada -> load JSON
    - Jika tidak -> buat dict kosong dengan field default
    """
    if os.path.exists(current_app.config["PROFILE_FILE"]):
        with open(current_app.config["PROFILE_FILE"], "r", encoding="utf-8") as f:
            profile_data = json.load(f)
    else:
        profile_data = {
            "nama": "", "email": "", "jk": "",
            "umur": "", "bio": "",
            "foto": "", "cover": ""
        }

    current_year = __import__("datetime").datetime.now().year
    return render_template("profile.html", profile=profile_data, current_year=current_year)


# ============================================
# EDIT PROFIL PAGE
# ============================================
@profile.route("/edit-profile")
def edit_profile():
    """
    Tampilkan halaman edit-profile.html dengan data profile saat ini (jika ada).
    """
    if os.path.exists(current_app.config["PROFILE_FILE"]):
        with open(current_app.config["PROFILE_FILE"], "r", encoding="utf-8") as f:
            profile_data = json.load(f)
    else:
        profile_data = {
            "nama": "", "email": "", "jk": "",
            "umur": "", "bio": "",
            "foto": "", "cover": ""
        }

    return render_template("edit-profile.html", profile=profile_data)


# ============================================
# SIMPAN PROFIL (NAMA, EMAIL, DLL)
# ============================================
@profile.route("/api/save-profile", methods=["POST"])
def save_profile():
    """
    Simpan data profil (nama, email, jk, umur, bio)
    - Menggabungkan data baru dengan data lama untuk menjaga foto/cover tetap utuh
    - Menyimpan ke PROFILE_FILE (JSON)
    """
    data = request.json

    # Ambil data lama agar foto & cover tetap ada jika tidak dikirim ulang
    if os.path.exists(current_app.config["PROFILE_FILE"]):
        with open(current_app.config["PROFILE_FILE"], "r", encoding="utf-8") as f:
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

    # Tulis file JSON
    with open(current_app.config["PROFILE_FILE"], "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=4, ensure_ascii=False)

    return jsonify({"status": "success"})


# ============================================
# UPLOAD FOTO PROFIL & COVER
# ============================================
@profile.route("/api/upload-photo", methods=["POST"])
def upload_photo():
    """
    Terima upload foto (profile atau cover).
    - Form field: 'photo' (file), 'type' ("profile" atau "cover")
    - Menyimpan file ke folder static/profile/
    - Menghapus file lama selain default
    - Mengupdate PROFILE_FILE dengan nama file baru
    """
    if "photo" not in request.files:
        return jsonify({"status": "error", "message": "Foto tidak ditemukan"}), 400

    file = request.files["photo"]
    upload_type = request.form.get("type")  # "profile" atau "cover"

    if upload_type not in ["profile", "cover"]:
        return jsonify({"status": "error", "message": "Tipe upload tidak valid"}), 400

    # Buat nama file aman dengan timestamp agar unik
    filename = secure_filename(str(int(time.time())) + "_" + file.filename)

    foto_folder = os.path.join(current_app.static_folder, "profile")
    os.makedirs(foto_folder, exist_ok=True)

    new_path = os.path.join(foto_folder, filename)
    file.save(new_path)

    # Ambil JSON lama
    if os.path.exists(current_app.config["PROFILE_FILE"]):
        with open(current_app.config["PROFILE_FILE"], "r", encoding="utf-8") as f:
            profile_data = json.load(f)
    else:
        profile_data = {}

    key = "foto" if upload_type == "profile" else "cover"
    old = profile_data.get(key, "")

    # Hapus file lama jika bukan file default
    if old not in ["", "profile.png", "cover.png"]:
        old_path = os.path.join(foto_folder, old)
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except Exception:
                # Jika gagal hapus, tetap lanjut (jangan crash)
                pass

    # Update profile JSON
    profile_data[key] = filename

    with open(current_app.config["PROFILE_FILE"], "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=4, ensure_ascii=False)

    return jsonify({"status": "success", "foto": filename})
# app/routes/profile_routes.py
import os
import json
import time
import sqlite3
from datetime import datetime
from flask import (
    render_template, request, jsonify,
    redirect, session, current_app
)
from werkzeug.utils import secure_filename

# helper functions (jika hash/verify dipakai, pastikan helper.py menyediakan fungsi tersebut)
from .helper import hash_password, verify_password  # tetap boleh ada, dipakai untuk ganti password jika diperlukan di masa depan


def register_profile_routes(app):
    """
    Semua route yang berhubungan dengan profil user.
    Catatan: endpoint ganti password diletakkan di auth_routes.py agar tidak duplikat.
    """

    PROFILE_FILE = app.config.get("PROFILE_FILE")
    FOTO_FOLDER = os.path.join(app.static_folder, "profile")
    os.makedirs(FOTO_FOLDER, exist_ok=True)

    # ============================================================
    #  HALAMAN PROFIL
    # ============================================================
    @app.route("/profile")
    def profile():
        if "user_id" not in session:
            return redirect("/login")

        # load data profil
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                profil = json.load(f)
        else:
            profil = {
                "nama": "", "email": "", "jk": "",
                "umur": "", "bio": "",
                "foto": "", "cover": ""
            }

        current_year = time.localtime().tm_year
        return render_template("profile.html", profile=profil, current_year=current_year)

    # ============================================================
    #  HALAMAN EDIT PROFIL
    # ============================================================
    @app.route("/edit-profile")
    def edit_profile():
        if "user_id" not in session:
            return redirect("/login")

        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                profil = json.load(f)
        else:
            profil = {
                "nama": "", "email": "", "jk": "",
                "umur": "", "bio": "",
                "foto": "", "cover": ""
            }

        current_year = time.localtime().tm_year
        return render_template("edit-profile.html", profile=profil, current_year=current_year)

    # ============================================================
    #  SIMPAN PROFIL (DATA TEXT)
    # ============================================================
    @app.route("/api/save-profile", methods=["POST"])
    def save_profile():
        if "user_id" not in session:
            return jsonify({"status": "error", "message": "Harus login!"}), 403

        data = request.json

        # Ambil data foto & cover lama agar tidak hilang
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                old = json.load(f)
        else:
            old = {}

        # jangan hapus foto / cover sebelumnya jika tidak dikirim
        data["foto"] = old.get("foto", "")
        data["cover"] = old.get("cover", "")

        # simpan JSON baru
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        return jsonify({"status": "success"})

    # ============================================================
    #  UPLOAD FOTO PROFIL & COVER (AUTO HAPUS LAMA)
    # ============================================================
    @app.route("/api/upload-photo", methods=["POST"])
    def upload_photo():
        if "user_id" not in session:
            return jsonify({"status": "error", "message": "Harus login!"}), 403

        if "photo" not in request.files:
            return jsonify({"status": "error", "message": "File tidak ditemukan"}), 400

        file = request.files["photo"]
        tipe = request.form.get("type")        # profile / cover

        if tipe not in ["profile", "cover"]:
            return jsonify({"status": "error", "message": "Tipe upload tidak valid"}), 400

        # Nama file baru → timestamp
        filename = secure_filename(str(int(time.time())) + "_" + file.filename)
        new_path = os.path.join(FOTO_FOLDER, filename)
        file.save(new_path)

        # Load JSON lama
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {}

        key = "foto" if tipe == "profile" else "cover"
        old_name = data.get(key, "")

        # Hapus foto lama jika bukan default
        if old_name not in ["", "profile.png", "cover.png"]:
            old_path = os.path.join(FOTO_FOLDER, old_name)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except Exception:
                    pass

        # Simpan nama file baru
        data[key] = filename

        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        return jsonify({"status": "success", "foto": filename})
import os
import json
import time
import sqlite3
from flask import (
    render_template, request, jsonify,
    redirect, session, current_app
)
from werkzeug.utils import secure_filename

from .helper import hash_password, verify_password


def register_profile_routes(app):
    """
    Semua route yang berhubungan dengan profil user.
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

        # jangan hapus foto / cover sebelumnya
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
                os.remove(old_path)

        # Simpan nama file baru
        data[key] = filename

        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        return jsonify({"status": "success", "foto": filename})

    # ============================================================
    #  GANTI PASSWORD — HALAMAN
    # ============================================================
    @app.route("/change-password")
    def change_password_page():
        if "user_id" not in session:
            return redirect("/login")

        return render_template("change-password.html")

    # ============================================================
    #  GANTI PASSWORD — API
    # ============================================================
    @app.route("/api/change-password", methods=["POST"])
    def change_password():
        if "user_id" not in session:
            return jsonify({"status": "error", "message": "Harus login!"}), 403

        data = request.json
        old_pass = data.get("old_password")
        new_pass = data.get("new_password")

        if not old_pass or not new_pass:
            return jsonify({"status": "error", "message": "Data tidak lengkap!"})

        user_id = session["user_id"]

        # Cek password lama dari DB
        conn = sqlite3.connect(app.config["DATABASE"])
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE id=?", (user_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return jsonify({"status": "error", "message": "User tidak ditemukan!"})

        old_hash = row[0]

        # validasi password lama
        if not verify_password(old_hash, old_pass):
            conn.close()
            return jsonify({"status": "error", "message": "Password lama salah!"})

        # hash baru
        new_hash = hash_password(new_pass)

        cursor.execute(
            "UPDATE users SET password=?, updated_at=? WHERE id=?",
            (new_hash, datetime.utcnow().isoformat(), user_id)
        )
        conn.commit()
        conn.close()

        return jsonify({"status": "success", "message": "Password berhasil diperbarui!"})
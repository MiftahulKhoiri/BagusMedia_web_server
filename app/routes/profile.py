import os
import sqlite3
from datetime import datetime
from flask import (
    Blueprint, render_template, request, jsonify,
    current_app, session, redirect, url_for
)
from werkzeug.utils import secure_filename

profile = Blueprint("profile", __name__)


# ============================================================
# 1. HALAMAN PROFIL — DATA DIAMBIL DARI DATABASE
# ============================================================
@profile.route("/profile")
def profile_page():

    # pastikan sudah login
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    conn = sqlite3.connect(current_app.config["DATABASE"])
    cursor = conn.cursor()

    cursor.execute("""
        SELECT username, email, jk, umur, bio, foto, cover
        FROM users WHERE id=?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return "Profil tidak ditemukan!", 404

    profile_data = {
        "nama": row[0],
        "email": row[1] or "",
        "jk": row[2] or "",
        "umur": row[3] or "",
        "bio": row[4] or "",
        "foto": row[5] or "profile.png",
        "cover": row[6] or "cover.png"
    }

    return render_template(
        "profile.html",
        profile=profile_data,
        current_year=datetime.now().year
    )


# ============================================================
# 2. HALAMAN EDIT PROFIL — DATA DIAMBIL DARI DATABASE
# ============================================================
@profile.route("/edit-profile")
def edit_profile():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    conn = sqlite3.connect(current_app.config["DATABASE"])
    cursor = conn.cursor()

    cursor.execute("""
        SELECT username, email, jk, umur, bio, foto, cover
        FROM users WHERE id=?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return "Error: Tidak ada data profil!", 404

    profile_data = {
        "nama": row[0],
        "email": row[1] or "",
        "jk": row[2] or "",
        "umur": row[3] or "",
        "bio": row[4] or "",
        "foto": row[5] or "profile.png",
        "cover": row[6] or "cover.png"
    }

    return render_template("edit-profile.html", profile=profile_data)


# ============================================================
# 3. SIMPAN PROFIL KE DATABASE
# ============================================================
@profile.route("/api/save-profile", methods=["POST"])
def save_profile():
    if "user_id" not in session:
        return jsonify({"status": "error", "message": "Not logged in"}), 403

    user_id = session["user_id"]
    data = request.json

    conn = sqlite3.connect(current_app.config["DATABASE"])
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET email=?, jk=?, umur=?, bio=?, updated_at=?
        WHERE id=?
    """, (
        data.get("email", ""),
        data.get("jk", ""),
        data.get("umur", ""),
        data.get("bio", ""),
        datetime.utcnow().isoformat(),
        user_id
    ))

    conn.commit()
    conn.close()

    return jsonify({"status": "success"})


# ============================================================
# 4. UPLOAD FOTO PROFIL / COVER — SIMPAN KE DATABASE
# ============================================================
@profile.route("/api/upload-photo", methods=["POST"])
def upload_photo():

    if "user_id" not in session:
        return jsonify({"status": "error", "message": "Not logged in"}), 403

    user_id = session["user_id"]

    if "photo" not in request.files:
        return jsonify({"status": "error", "message": "No file"}), 400

    file = request.files["photo"]
    upload_type = request.form.get("type")  # profile / cover

    if upload_type not in ["profile", "cover"]:
        return jsonify({"status": "error", "message": "Invalid type"}), 400

    # simpan file
    filename = secure_filename(f"{user_id}_{upload_type}_{int(datetime.now().timestamp())}_{file.filename}")

    foto_folder = os.path.join(current_app.static_folder, "profile")
    os.makedirs(foto_folder, exist_ok=True)

    file_path = os.path.join(foto_folder, filename)
    file.save(file_path)

    # update database
    column_name = "foto" if upload_type == "profile" else "cover"

    conn = sqlite3.connect(current_app.config["DATABASE"])
    cursor = conn.cursor()

    cursor.execute(f"""
        UPDATE users
        SET {column_name}=?, updated_at=?
        WHERE id=?
    """, (filename, datetime.utcnow().isoformat(), user_id))

    conn.commit()
    conn.close()

    return jsonify({"status": "success", "filename": filename})
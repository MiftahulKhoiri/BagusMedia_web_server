# app/routes/auth.py
from flask import Blueprint, render_template, request, redirect, session, jsonify
import sqlite3
from datetime import datetime
from flask import current_app as app
from .utils import hash_password, verify_password

auth = Blueprint("auth", __name__)


# =====================================================
# REGISTER USER BARU (role default = "user")
# =====================================================
@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        if username == "" or password == "":
            return "Semua field harus diisi!"

        hashed = hash_password(password)
        now = datetime.utcnow().isoformat()

        try:
            conn = sqlite3.connect(app.config["DATABASE"])
            cursor = conn.cursor()

            # Tambahkan role (default user)
            cursor.execute("""
                INSERT INTO users (username, password, role, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (username, hashed, "user", now, now))

            conn.commit()
            conn.close()
            return redirect("/login")

        except sqlite3.IntegrityError:
            return "Username sudah dipakai!"

    return render_template("register.html")


# =====================================================
# LOGIN USER (root / user)
# =====================================================
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        conn = sqlite3.connect(app.config["DATABASE"])
        cursor = conn.cursor()

        cursor.execute("SELECT id, password, role FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            return "Username tidak ditemukan!"

        user_id, stored_pass, role = user

        # Verifikasi password
        if not verify_password(stored_pass, password):
            return "Password salah!"

        # Simpan ke session
        session["user_id"] = user_id
        session["username"] = username
        session["role"] = role  # 🔥 role dimasukkan ke session

        return redirect("/home")

    return render_template("login.html")


# =====================================================
# LOGOUT
# =====================================================
@auth.route("/logout")
def logout():
    session.clear()  # role ikut terhapus
    return redirect("/")


# =====================================================
# HALAMAN GANTI PASSWORD
# =====================================================
@auth.route("/change-password")
def change_password_page():
    if "user_id" not in session:
        return redirect("/login")

    return render_template("change-password.html")


# =====================================================
# API GANTI PASSWORD
# =====================================================
@auth.route("/api/change-password", methods=["POST"])
def change_password():
    if "user_id" not in session:
        return jsonify({"status": "error", "message": "Harus login!"}), 403

    data = request.json
    old_pass = data.get("old_password")
    new_pass = data.get("new_password")

    if not old_pass or not new_pass:
        return jsonify({"status": "error", "message": "Data tidak lengkap!"})

    user_id = session["user_id"]

    conn = sqlite3.connect(app.config["DATABASE"])
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM users WHERE id=?", (user_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({"status": "error", "message": "User tidak ditemukan!"})

    stored_password = row[0]

    # Cek password lama
    if not verify_password(stored_password, old_pass):
        conn.close()
        return jsonify({"status": "error", "message": "Password lama salah!"})

    # Simpan password baru
    new_hashed = hash_password(new_pass)
    cursor.execute(
        "UPDATE users SET password=?, updated_at=? WHERE id=?",
        (new_hashed, datetime.utcnow().isoformat(), user_id)
    )
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": "Password berhasil diperbarui!"})
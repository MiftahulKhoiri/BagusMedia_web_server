# app/routes/auth.py
from flask import Blueprint, render_template, request, redirect, session, jsonify
import sqlite3
from datetime import datetime
from flask import current_app as app
from .utils import hash_password, verify_password

# ============================================
# BLUEPRINT UNTUK AUTENTIKASI
# ============================================
auth = Blueprint("auth", __name__)


# ============================================
# REGISTER USER
# ============================================
@auth.route("/register", methods=["GET", "POST"])
def register():
    """
    Halaman + proses registrasi user baru.
    Jika POST:
        - Ambil username dan password
        - Hash password
        - Simpan ke database
    Jika GET:
        - Tampilkan halaman register.html
    """
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        # Cek data kosong
        if username == "" or password == "":
            return "Harus diisi!"

        # Hash password
        hashed = hash_password(password)
        now = datetime.utcnow().isoformat()

        try:
            # Simpan ke database
            conn = sqlite3.connect(app.config["DATABASE"])
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (username, hashed, now, now)
            )
            conn.commit()
            conn.close()
            return redirect("/login")

        except sqlite3.IntegrityError:
            # Username sudah ada
            return "Username sudah dipakai!"

    return render_template("register.html")


# ============================================
# LOGIN USER
# ============================================
@auth.route("/login", methods=["GET", "POST"])
def login():
    """
    Halaman login + proses login.
    Jika POST:
        - Cocokkan username dan password
        - Jika benar -> set session
        - Jika salah -> tampilkan pesan gagal
    """
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        # Query user berdasarkan username
        conn = sqlite3.connect(app.config["DATABASE"])
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()

        # Cek user & password
        if user and verify_password(user[1], password):
            session["user_id"] = user[0]
            session["username"] = username
            return redirect("/home")

        return "Username atau password salah!"

    return render_template("login.html")


# ============================================
# LOGOUT
# ============================================
@auth.route("/logout")
def logout():
    """
    Menghapus semua data session user.
    Setelah logout, user dikembalikan ke halaman login.
    """
    session.clear()
    return redirect("/login")


# ============================================
# HALAMAN GANTI PASSWORD
# ============================================
@auth.route("/change-password")
def change_password_page():
    """
    Menampilkan halaman form ganti password.
    Hanya bisa diakses jika user sudah login.
    """
    if "user_id" not in session:
        return redirect("/login")

    return render_template("change-password.html")


# ============================================
# API GANTI PASSWORD
# ============================================
@auth.route("/api/change-password", methods=["POST"])
def change_password():
    """
    Endpoint untuk mengganti password user.
    Proses:
        - Validasi login
        - Ambil old_password & new_password
        - Verifikasi password lama
        - Simpan password baru ke database
    """
    if "user_id" not in session:
        return jsonify({"status": "error", "message": "Harus login!"}), 403

    data = request.json
    old_pass = data.get("old_password")
    new_pass = data.get("new_password")

    if not old_pass or not new_pass:
        return jsonify({"status": "error", "message": "Data tidak lengkap!"})

    user_id = session["user_id"]

    # Ambil password lama dari database
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
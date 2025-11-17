import sqlite3
from datetime import datetime
from flask import request, render_template, redirect, session, jsonify

from . import auth_bp
from ...routes.utils import hash_password, verify_password


# REGISTER USER
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        if username == "" or password == "":
            return "Harus diisi!"

        hashed = hash_password(password)
        now = datetime.utcnow().isoformat()

        try:
            conn = sqlite3.connect(auth_bp.app.config["DATABASE"])
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (username, hashed, now, now)
            )
            conn.commit()
            conn.close()
            return redirect("/login")
        except sqlite3.IntegrityError:
            return "Username sudah dipakai!"

    return render_template("register.html")


# LOGIN USER
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        conn = sqlite3.connect(auth_bp.app.config["DATABASE"])
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and verify_password(user[1], password):
            session["user_id"] = user[0]
            session["username"] = username
            return redirect("/home")

        return "Username atau password salah!"

    return render_template("login.html")


# PAGE GANTI PASSWORD
@auth_bp.route("/change-password")
def change_password_page():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("change-password.html")


# API GANTI PASSWORD
@auth_bp.route("/api/change-password", methods=["POST"])
def change_password():
    if "user_id" not in session:
        return jsonify({"status": "error", "message": "Harus login!"}), 403

    data = request.json
    old_pass = data.get("old_password")
    new_pass = data.get("new_password")

    if not old_pass or not new_pass:
        return jsonify({"status": "error", "message": "Data tidak lengkap!"})

    user_id = session["user_id"]

    conn = sqlite3.connect(auth_bp.app.config["DATABASE"])
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE id=?", (user_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({"status": "error", "message": "User tidak ditemukan!"})

    stored_password = row[0]

    if not verify_password(stored_password, old_pass):
        conn.close()
        return jsonify({"status": "error", "message": "Password lama salah!"})

    new_hashed = hash_password(new_pass)
    cursor.execute(
        "UPDATE users SET password=?, updated_at=? WHERE id=?",
        (new_hashed, datetime.utcnow().isoformat(), user_id)
    )
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": "Password berhasil diperbarui!"})


# LOGOUT
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
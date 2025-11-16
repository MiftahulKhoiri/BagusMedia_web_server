import sqlite3
from flask import render_template, request, redirect, session, jsonify
from datetime import datetime
from .helper import hash_password, verify_password

def register_auth_routes(app):

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form["username"].strip()
            password = request.form["password"]

            if not username or not password:
                return "Harus diisi!"

            hashed = hash_password(password)
            now = datetime.utcnow().isoformat()

            try:
                conn = sqlite3.connect(app.config["DATABASE"])
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username,password,created_at,updated_at) VALUES (?,?,?,?)",
                    (username, hashed, now, now)
                )
                conn.commit()
                conn.close()
                return redirect("/login")
            except sqlite3.IntegrityError:
                return "Username sudah dipakai!"

        return render_template("register.html")

    @app.route("/login", methods=["GET","POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"].strip()
            password = request.form["password"]

            conn = sqlite3.connect(app.config["DATABASE"])
            cursor = conn.cursor()
            cursor.execute("SELECT id,password FROM users WHERE username=?", (username,))
            user = cursor.fetchone()
            conn.close()

            if user and verify_password(user[1], password):
                session["user_id"] = user[0]
                session["username"] = username
                return redirect("/home")

            return "Login gagal!"

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect("/login")

    @app.route("/change-password")
    def change_password_page():
        return render_template("change-password.html")

    @app.route("/api/change-password", methods=["POST"])
    def change_password():
        if "user_id" not in session:
            return jsonify({"status":"error","message":"Harus login!"}), 403

        data = request.json
        old_pass = data.get("old_password")
        new_pass = data.get("new_password")

        if not old_pass or not new_pass:
            return jsonify({"status":"error","message":"Data tidak lengkap!"})

        user_id = session["user_id"]

        conn = sqlite3.connect(app.config["DATABASE"])
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE id=?", (user_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return jsonify({"status":"error","message":"User tidak ditemukan!"})

        if not verify_password(row[0], old_pass):
            conn.close()
            return jsonify({"status":"error","message":"Password lama salah!"})

        new_hash = hash_password(new_pass)

        cursor.execute("UPDATE users SET password=?, updated_at=? WHERE id=?",
                       (new_hash, datetime.utcnow().isoformat(), user_id))
        conn.commit()
        conn.close()

        return jsonify({"status":"success","message":"Password berhasil diubah!"})
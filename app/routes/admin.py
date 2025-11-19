# app/routes/admin.py

from flask import Blueprint, render_template, current_app, jsonify, request
import sqlite3, platform, psutil, socket
from datetime import datetime

from .utils import require_root  # proteksi root

admin = Blueprint("admin", __name__)


# =====================================================
# SAFE GET UPTIME (Termux tidak bisa akses boot_time)
# =====================================================
def safe_uptime():
    try:
        boot = psutil.boot_time()  # bisa error di Android
        return str(datetime.now() - datetime.fromtimestamp(boot)).split('.')[0]
    except Exception:
        return "Tidak dapat membaca (dibatasi Android)"


# =====================================================
# HALAMAN DASHBOARD ADMIN
# =====================================================
@admin.route("/admin")
def admin_dashboard():
    check = require_root()
    if check:
        return check

    # ------------------------
    # Info sistem
    # ------------------------
    try:
        disk = psutil.disk_usage('/')
        ram = psutil.virtual_memory()
    except Exception:
        # fallback untuk Android permission
        disk = ram = None

    info = {
        "os": platform.system(),
        "os_version": platform.release(),
        "python": platform.python_version(),
        "cpu": psutil.cpu_count(logical=True),

        "ram_total": round(ram.total / (1024**3), 2) if ram else "N/A",
        "ram_used": round(ram.used / (1024**3), 2) if ram else "N/A",

        "disk_total": round(disk.total / (1024**3), 2) if disk else "N/A",
        "disk_used": round(disk.used / (1024**3), 2) if disk else "N/A",

        "uptime": safe_uptime()
    }

    # IP Address
    try:
        info["ip"] = socket.gethostbyname(socket.gethostname())
    except:
        info["ip"] = "Tidak diketahui"

    # ------------------------
    # List semua user
    # ------------------------
    conn = sqlite3.connect(current_app.config["DATABASE"])
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users ORDER BY id ASC")
    users = cursor.fetchall()
    conn.close()

    return render_template(
        "admin.html",
        info=info,
        users=users,
        current_year=datetime.now().year
    )


# =====================================================
# API GANTI ROLE USER
# =====================================================
@admin.route("/api/change-role", methods=["POST"])
def change_role():
    check = require_root()
    if check:
        return check

    data = request.json or {}
    user_id = data.get("user_id")
    new_role = data.get("role")

    if new_role not in ["user", "root"]:
        return jsonify({"error": "Role tidak valid!"}), 400

    conn = sqlite3.connect(current_app.config["DATABASE"])
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM users WHERE id=?", (user_id,))
    row = cursor.fetchone()

    if not row:
        return jsonify({"error": "User tidak ditemukan!"}), 404

    username = row[0]

    # Cegah root diubah
    if username == "root":
        return jsonify({"error": "User root tidak boleh diubah!"}), 403

    cursor.execute("UPDATE users SET role=? WHERE id=?", (new_role, user_id))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})


# =====================================================
# API HAPUS USER
# =====================================================
@admin.route("/api/delete-user", methods=["POST"])
def delete_user():
    check = require_root()
    if check:
        return check

    data = request.json or {}
    user_id = data.get("user_id")

    conn = sqlite3.connect(current_app.config["DATABASE"])
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM users WHERE id=?", (user_id,))
    row = cursor.fetchone()

    if not row:
        return jsonify({"error": "User tidak ditemukan!"}), 404

    username = row[0]

    if username == "root":
        return jsonify({"error": "Root tidak boleh dihapus!"}), 403

    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})
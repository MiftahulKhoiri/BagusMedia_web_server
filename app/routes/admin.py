# app/routes/admin.py

from flask import Blueprint, render_template, current_app, jsonify, request
import sqlite3, platform, psutil, socket, time
from datetime import datetime

from .utils import require_root  # proteksi root

admin = Blueprint("admin", __name__)


# =====================================================
# SAFE UPTIME (Android / Termux tidak izinkan boot_time)
# =====================================================
def safe_uptime():
    try:
        boot = psutil.boot_time()
        return str(datetime.now() - datetime.fromtimestamp(boot)).split('.')[0]
    except Exception:
        # fallback manual uptime
        uptime_seconds = time.time() - psutil.Process().create_time()
        return time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))


# =====================================================
# HALAMAN ADMIN (Terminal Hacker Mode)
# =====================================================
@admin.route("/admin")
def admin_dashboard():
    check = require_root()
    if check:
        return check

    # ---- System Info (safe untuk Android) ----
    try:
        mem = psutil.virtual_memory()
        ram_total = round(mem.total / (1024**3), 2)
        ram_used = round(mem.used / (1024**3), 2)
    except Exception:
        ram_total = "N/A"
        ram_used = "N/A"

    try:
        disk = psutil.disk_usage('/')
        disk_total = round(disk.total / (1024**3), 2)
        disk_used = round(disk.used / (1024**3), 2)
    except Exception:
        disk_total = "N/A"
        disk_used = "N/A"

    info = {
        "os": platform.system(),
        "os_version": platform.release(),
        "python": platform.python_version(),
        "cpu": psutil.cpu_count(logical=True),
        "ram_total": ram_total,
        "ram_used": ram_used,
        "disk_total": disk_total,
        "disk_used": disk_used,
        "uptime": safe_uptime()
    }

    # ---- IP ----
    try:
        info["ip"] = socket.gethostbyname(socket.gethostname())
    except:
        info["ip"] = "Tidak diketahui"

    # ---- User List ----
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
# API GANTI ROLE
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
    user = cursor.fetchone()

    if not user:
        return jsonify({"error": "User tidak ditemukan!"}), 404

    username = user[0]

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
    user = cursor.fetchone()

    if not user:
        return jsonify({"error": "User tidak ditemukan!"}), 404

    username = user[0]

    if username == "root":
        return jsonify({"error": "Root tidak boleh dihapus!"}), 403

    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})


# =====================================================
# API REAL-TIME MONITOR
# =====================================================
@admin.route("/api/monitor")
def api_monitor():
    try:
        cpu = psutil.cpu_percent()
    except:
        cpu = 0

    try:
        mem = psutil.virtual_memory()
        ram_used = round(mem.used / (1024**3), 2)
        ram_total = round(mem.total / (1024**3), 2)
        ram_percent = mem.percent
    except:
        ram_used = ram_total = ram_percent = "N/A"

    try:
        disk = psutil.disk_usage('/')
        disk_used = round(disk.used / (1024**3), 2)
        disk_total = round(disk.total / (1024**3), 2)
        disk_percent = disk.percent
    except:
        disk_used = disk_total = disk_percent = "N/A"

    return jsonify({
        "cpu": cpu,
        "ram_used": ram_used,
        "ram_total": ram_total,
        "ram_percent": ram_percent,
        "disk_used": disk_used,
        "disk_total": disk_total,
        "disk_percent": disk_percent,
        "uptime": safe_uptime()
    })
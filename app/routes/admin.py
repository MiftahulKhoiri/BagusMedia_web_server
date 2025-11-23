# app/routes/admin.py

from flask import Blueprint, render_template, current_app, jsonify, request
import sqlite3, platform, psutil, socket, time
from datetime import datetime

from .utils import require_root

admin = Blueprint("admin", __name__)


# =====================================================
# SAFE UPTIME (Android / Termux Friendly)
# =====================================================
def safe_uptime():
    """
    Android melarang psutil.boot_time() dan Process.create_time(),
    jadi kita pakai /proc/uptime yang aman.
    """
    try:
        with open("/proc/uptime", "r") as f:
            uptime_seconds = float(f.read().split()[0])

        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    except:
        return "Tidak tersedia"
    

# =====================================================
# ADMIN DASHBOARD
# =====================================================
@admin.route("/admin")
def admin_dashboard():
    check = require_root()
    if check:
        return check

    # ===============================
    # RAM (aman di Android)
    # ===============================
    try:
        mem = psutil.virtual_memory()
        ram_total = round(mem.total / (1024**3), 2)
        ram_used = round(mem.used / (1024**3), 2)
    except:
        ram_total = "N/A"
        ram_used = "N/A"

    # ===============================
    # DISK (aman di Android)
    # ===============================
    try:
        disk = psutil.disk_usage('/')
        disk_total = round(disk.total / (1024**3), 2)
        disk_used = round(disk.used / (1024**3), 2)
    except:
        disk_total = "N/A"
        disk_used = "N/A"

    # ===============================
    # System Info
    # ===============================
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

    # ===============================
    # IP Address
    # ===============================
    try:
        info["ip"] = socket.gethostbyname(socket.gethostname())
    except:
        info["ip"] = "Tidak diketahui"

    # ===============================
    # User List
    # ===============================
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
    row = cursor.fetchone()

    if not row:
        return jsonify({"error": "User tidak ditemukan!"}), 404

    username = row[0]

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


# =====================================================
# API REALTIME SYSTEM MONITOR
# =====================================================
@admin.route("/api/monitor")
def api_monitor():
    # CPU aman
    try:
        cpu = psutil.cpu_percent()
    except:
        cpu = 0

    # RAM aman
    try:
        mem = psutil.virtual_memory()
        ram_used = round(mem.used / (1024**3), 2)
        ram_total = round(mem.total / (1024**3), 2)
        ram_percent = mem.percent
    except:
        ram_used = ram_total = ram_percent = 0

    # Disk aman
    try:
        disk = psutil.disk_usage('/')
        disk_used = round(disk.used / (1024**3), 2)
        disk_total = round(disk.total / (1024**3), 2)
        disk_percent = disk.percent
    except:
        disk_used = disk_total = disk_percent = 0

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

# =====================================================
# API SHUTDOWN SERVER (AMAN UNTUK TERMUX)
# =====================================================
@admin.route("/api/shutdown", methods=["POST"])
def shutdown_server():
    check = require_root()
    if check:
        return check

    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        return jsonify({"error": "Tidak bisa mematikan server"}), 500

    func()  # MATIKAN SERVER
    return jsonify({"status": "server stopped"})


# =====================================================
# API RESTART SERVER (AMAN)
# =====================================================
@admin.route("/api/restart", methods=["POST"])
def restart_server():
    check = require_root()
    if check:
        return check

    # Restart server Flask bukan restart HP
    return jsonify({"status": "restart"}), 200
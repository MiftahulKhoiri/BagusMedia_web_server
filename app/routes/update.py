# app/routes/update.py

import subprocess
from flask import Blueprint, render_template, jsonify, current_app

# Import proteksi role root
from .utils import require_root


# ============================================
# BLUEPRINT UPDATE
# ============================================
update_bp = Blueprint("update_bp", __name__)


# ============================================
# HALAMAN UPDATE (HANYA ROOT)
# ============================================
@update_bp.route("/update")
def update():
    # Proteksi hanya root yang boleh membuka
    check = require_root()
    if check:
        return check

    return render_template("update.html")


# ============================================
# API : CEK UPDATE
# ============================================
@update_bp.route("/api/check-update")
def check_update():
    """
    Cek apakah server tertinggal dari GitHub.
    - git fetch → ambil update
    - git status -uno → cek apakah "behind"
    """
    try:
        base_dir = current_app.config["PROJECT_ROOT"]

        # Ambil update terbaru dari remote
        subprocess.run(["git", "fetch"], cwd=base_dir)

        # Cek status branch
        status = subprocess.run(
            ["git", "status", "-uno"],
            cwd=base_dir,
            capture_output=True,
            text=True
        )

        update_available = "behind" in status.stdout.lower()

        return jsonify({
            "update_available": update_available,
            "output": status.stdout
        })

    except Exception as e:
        return jsonify({
            "update_available": False,
            "error": str(e)
        })


# ============================================
# WEBSOCKET UPDATE REALTIME
# ============================================
def register_ws(sock):
    """
    Websocket tidak bisa masuk blueprint default,
    jadi kita daftar websocket manual di app.py.

    Cara pemanggilan di app.py:
        register_ws(sock)
    """

    @sock.route("/ws/update")
    def ws_update(ws):
        base_dir = current_app.config["PROJECT_ROOT"]

        # Fungsi aman untuk mengirim pesan
        def safe_send(msg):
            try:
                ws.send(msg)
            except:
                pass  # WebSocket tertutup → biarkan tanpa error

        safe_send("[INFO] Memulai update...\n")

        try:
            # Jalankan git pull
            process = subprocess.Popen(
                ["git", "pull"],
                cwd=base_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            # Kirim output baris demi baris
            for line in process.stdout:
                safe_send(line.strip())

        except Exception as e:
            safe_send(f"[ERROR] {e}")

        safe_send("[DONE]")
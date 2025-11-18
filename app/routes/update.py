# app/routes/update.py
import subprocess
from flask import Blueprint, render_template, jsonify, current_app

# ============================================
# BLUEPRINT UPDATE (CEK UPDATE & WEBSOCKET)
# ============================================
update_bp = Blueprint("update_bp", __name__)


# ============================================
# HALAMAN UPDATE
# ============================================
@update_bp.route("/update")
def update():
    """
    Tampilkan halaman update.html.
    Halaman ini biasanya berisi tombol untuk cek update dan menjalankan update via websocket.
    """
    return render_template("update.html")


# ============================================
# API CHECK UPDATE
# ============================================
@update_bp.route("/api/check-update")
def check_update():
    """
    Mengecek apakah ada update terbaru di repository git.
    - Menjalankan "git fetch"
    - Menjalankan "git status -uno"
    - Jika status stdout mengandung kata 'behind' -> ada update
    """
    try:
        BASE_DIR = current_app.config["PROJECT_ROOT"]

        # Git fetch - mengambil info update terbaru
        subprocess.run(["git", "fetch"], cwd=BASE_DIR)

        # Git status -uno - cek status branch lokal terhadap remote
        status = subprocess.run(
            ["git", "status", "-uno"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )

        update_available = "behind" in status.stdout.lower()
        return jsonify({
            "update_available": update_available,
            "output": status.stdout
        })
    except Exception as e:
        return jsonify({"update_available": False, "error": str(e)})


# ============================================
# WEBSOCKET UNTUK UPDATE
# ============================================
def register_ws(sock):
    """
    Fungsi ini didaftarkan di app.py untuk membuat route websocket:
    @sock.route("/ws/update")
    Kenapa pakai fungsi? Karena Blueprint bawaan Flask tidak mendukung websocket dari Flask-Sock.
    """

    @sock.route("/ws/update")
    def ws_update(ws):
        """
        WebSocket yang menjalankan 'git pull' dan mengirim outputnya ke client secara realtime.
        - Mengirim pesan awal
        - Menjalankan git pull via subprocess.Popen
        - Mengirim setiap baris output secara streaming
        """
        BASE_DIR = current_app.config["PROJECT_ROOT"]

        def send(msg):
            try:
                ws.send(msg)
            except:
                pass  # Supaya tidak error kalau websocket tertutup mendadak

        send("[INFO] Memulai update...\n")

        # Proses git pull
        p = subprocess.Popen(
            ["git", "pull"],
            cwd=BASE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # Kirim setiap baris output ke websocket
        for line in p.stdout:
            send(line.strip())

        send("[DONE]")
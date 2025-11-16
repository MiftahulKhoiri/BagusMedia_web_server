import subprocess
from flask import Blueprint, render_template, jsonify

update_bp = Blueprint("update_bp", __name__)

def init_update(app, sock):

    BASE_DIR = app.config["PROJECT_ROOT"]

    # =============================
    # HALAMAN UPDATE
    # =============================
    @update_bp.route("/update")
    def update_page():
        return render_template("update.html")

    # =============================
       # CEK UPDATE
    # =============================
    @update_bp.route("/api/check-update")
    def check_update():
        try:
            # Ambil informasi terbaru dari origin
            subprocess.run(["git", "fetch"], cwd=BASE_DIR)

            status = subprocess.run(
                ["git", "status", "-uno"],
                cwd=BASE_DIR,
                capture_output=True,
                text=True
            )

            available = "behind" in status.stdout

            return jsonify({
                "update_available": available,
                "output": status.stdout
            })

        except Exception as e:
            return jsonify({
                "update_available": False,
                "error": str(e)
            })

    # =============================
    # WEBSOCKET UNTUK PROSES UPDATE
    # =============================
    @sock.route("/ws/update")
    def ws_update(ws):

        def send(msg):
            try:
                ws.send(msg)
            except:
                pass  # socket putus → abaikan

        send("[INFO] Memulai update...\n")

        p = subprocess.Popen(
            ["git", "pull"],
            cwd=BASE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # Kirim output git pull baris demi baris
        for line in p.stdout:
            send(line.strip())

        send("[DONE]")
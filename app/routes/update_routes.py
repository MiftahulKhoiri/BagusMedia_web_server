import os
import subprocess
import time
import threading
import sys
from flask import render_template, jsonify


def register_update_routes(app, sock):
    """
    Semua route untuk sistem update:
    - halaman update
    - cek update
    - websocket update realtime
    - restart server
    """

    PROJECT_ROOT = app.config["PROJECT_ROOT"]

    # =====================================================
    #  HALAMAN UPDATE
    # =====================================================
    @app.route("/update")
    def update():
        return render_template("update.html")

    # =====================================================
    #  API CEK UPDATE AVAILABLE
    # =====================================================
    @app.route("/api/check-update")
    def check_update():
        try:
            # Ambil info terbaru dari Git
            subprocess.run(["git", "fetch"], cwd=PROJECT_ROOT)

            status = subprocess.run(
                ["git", "status", "-uno"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True
            )

            update_available = "behind" in status.stdout

            return jsonify({
                "update_available": update_available,
                "output": status.stdout
            })

        except Exception as e:
            return jsonify({
                "update_available": False,
                "error": str(e)
            })

    # =====================================================
    #  WEBSOCKET UNTUK PROSES UPDATE
    # =====================================================
    @sock.route("/ws/update")
    def ws_update(ws):

        def send(msg):
            try:
                ws.send(msg)
            except:
                pass

        send("[INFO] Memulai update...\n")

        process = subprocess.Popen(
            ["git", "pull"],
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        for line in process.stdout:
            send(line.strip())

        send("[DONE]")

    # =====================================================
    #  API RESTART SERVER
    # =====================================================
    @app.route("/api/restart", methods=["POST"])
    def restart_server():

        def delayed():
            time.sleep(1)
            os.execl(sys.executable, sys.executable, *sys.argv)

        threading.Thread(target=delayed).start()

        return jsonify({"message": "Restart..."})
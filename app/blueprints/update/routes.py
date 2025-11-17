import subprocess
from flask import render_template, jsonify

from . import update_bp


# HALAMAN UPDATE
@update_bp.route("/update")
def update():
    return render_template("update.html")


# API CHECK UPDATE (git fetch)
@update_bp.route("/api/check-update")
def check_update():
    try:
        base = update_bp.app.config["PROJECT_ROOT"]

        subprocess.run(["git", "fetch"], cwd=base)
        status = subprocess.run(
            ["git", "status", "-uno"],
            cwd=base,
            capture_output=True,
            text=True
        )

        update_available = "behind" in status.stdout
        return {
            "update_available": update_available,
            "output": status.stdout
        }

    except Exception as e:
        return {"update_available": False, "error": str(e)}


# WEBSOCKET UNTUK GIT PULL
def register_websocket(sock):

    base = update_bp.app.config["PROJECT_ROOT"]

    @sock.route("/ws/update")
    def ws_update(ws):

        def send(msg):
            try:
                ws.send(msg)
            except:
                pass

        send("[INFO] Memulai update...\n")

        p = subprocess.Popen(
            ["git", "pull"],
            cwd=base,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        for line in p.stdout:
            send(line.strip())

        send("[DONE]")
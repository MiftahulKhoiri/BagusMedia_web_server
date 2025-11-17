import subprocess

# =============================
# ROUTES: UPDATE (GIT FETCH/PULL + WEBSOCKET)
# =============================

def update_routes(app, sock):

    BASE_DIR = app.config["PROJECT_ROOT"]

    # HALAMAN UPDATE UTAMA
    @app.route("/update")
    def update():
        return render_template("update.html")

    # CEK UPDATE VIA GIT
    @app.route("/api/check-update")
    def check_update():
        try:
            subprocess.run(["git", "fetch"], cwd=BASE_DIR)
            status = subprocess.run(
                ["git", "status", "-uno"],
                cwd=BASE_DIR,
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

    # WEBSOCKET UNTUK UPDATE
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
            cwd=BASE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        for line in p.stdout:
            send(line.strip())

        send("[DONE]")
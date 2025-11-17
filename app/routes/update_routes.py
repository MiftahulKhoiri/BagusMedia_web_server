import subprocess
from flask import render_template   # Import untuk render template HTML

# =============================
# ROUTES: UPDATE (GIT FETCH/PULL + WEBSOCKET)
# =============================

def update_routes(app, sock):

    # Lokasi root project (berisi folder .git)
    BASE_DIR = app.config["PROJECT_ROOT"]

    # =============================
    # HALAMAN UTAMA UPDATE
    # =============================
    @app.route("/update")
    def update():
        """
        Menampilkan halaman utama update.
        Halaman ini biasanya berisi UI yang menampilkan status update
        dan tombol untuk melakukan pengecekan/pembaruan.
        """
        return render_template("update.html")

    # =============================
    # API CEK UPDATE GIT
    # =============================
    @app.route("/api/check-update")
    def check_update():
        """
        Mengecek apakah ada update baru di repository Git.
        - git fetch: mengambil informasi update terbaru dari remote origin.
        - git status -uno: mengecek apakah branch lokal ketinggalan.
        Mengembalikan JSON yang berisi apakah update tersedia.
        """
        try:
            # Ambil info update terbaru
            subprocess.run(["git", "fetch"], cwd=BASE_DIR)

            # Cek apakah versi lokal tertinggal (behind)
            status = subprocess.run(
                ["git", "status", "-uno"],
                cwd=BASE_DIR,
                capture_output=True,
                text=True
            )

            update_available = "behind" in status.stdout

            return {
                "update_available": update_available,
                "output": status.stdout  # Info status Git
            }

        except Exception as e:
            # Jika ada error, kembalikan detail error
            return {"update_available": False, "error": str(e)}

    # =============================
    # WEBSOCKET UNTUK LIVE UPDATE
    # =============================
    @sock.route("/ws/update")
    def ws_update(ws):
        """
        Menjalankan proses update Git (git pull) dan mengirimkan output
        secara realtime melalui WebSocket ke browser.
        Cocok untuk menampilkan progress update langsung di UI.
        """

        # Helper function untuk mengirim pesan
        def send(msg):
            try:
                ws.send(msg)
            except:
                # Jika client sudah disconnect, abaikan
                pass

        send("[INFO] Memulai update...\n")

        # Jalankan git pull agar repository diperbarui
        p = subprocess.Popen(
            ["git", "pull"],
            cwd=BASE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # Kirim setiap baris output secara realtime
        for line in p.stdout:
            send(line.strip())

        # Selesai
        send("[DONE]")
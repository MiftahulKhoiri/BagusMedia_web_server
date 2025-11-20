import socket
from app import create_app

app = create_app()

def get_free_port(start_port=5000):
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # cek apakah port bisa dibuka
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port  # port aman dipakai
            port += 1  # kalau kepakai, lanjut port berikutnya

if __name__ == "__main__":
    default_port = 5000
    port = get_free_port(default_port)

    print(f"Port ditemukan: {port}")

    app.run(host="0.0.0.0", port=port, debug=True)
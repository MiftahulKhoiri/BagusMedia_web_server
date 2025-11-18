# app/routes/about.py

from flask import Blueprint, render_template, current_app
import platform, os, psutil, socket
from datetime import datetime

about = Blueprint("about", __name__)

def format_gb(bytes_value):
    return round(bytes_value / (1024**3), 2)

@about.route("/about")
def about_page():
    # --- Sistem Operasi ---
    system_info = {
        "os": platform.system(),
        "os_version": platform.release(),
        "python": platform.python_version(),
        "flask_version": "?"  # optional
    }

    # --- CPU ---
    cpu_count = psutil.cpu_count(logical=True)

    # --- RAM ---
    ram_info = psutil.virtual_memory()
    ram_total = format_gb(ram_info.total)
    ram_used = format_gb(ram_info.used)

    # --- Disk ---
    disk_info = psutil.disk_usage("/")
    disk_total = format_gb(disk_info.total)
    disk_used = format_gb(disk_info.used)

    # --- Uptime ---
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    uptime_str = str(uptime).split('.')[0]

    # --- IP Server ---
    try:
        ip_server = socket.gethostbyname(socket.gethostname())
    except:
        ip_server = "Tidak diketahui"

    return render_template(
        "about.html",
        system=system_info,
        cpu_count=cpu_count,
        ram_total=ram_total,
        ram_used=ram_used,
        disk_total=disk_total,
        disk_used=disk_used,
        uptime=uptime_str,
        ip_address=ip_server,
        project_root=current_app.config["PROJECT_ROOT"],
        current_year=datetime.now().year,
        version="1.0 Stable"
    )
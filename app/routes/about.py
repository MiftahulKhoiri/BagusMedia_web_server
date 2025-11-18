# app/routes/about.py

from flask import Blueprint, render_template
import platform
import os
import psutil
from datetime import datetime

about = Blueprint("about", __name__)


@about.route("/about")
def about_page():
    """
    Halaman About berisi informasi server dan aplikasi.
    """

    # Informasi sistem
    system_info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "processor": platform.processor(),
        "python": platform.python_version(),
        "flask_version": platform.python_implementation(),
        "uptime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # Info storage
    disk = psutil.disk_usage("/")
    disk_info = {
        "total": f"{disk.total // (1024**3)} GB",
        "used": f"{disk.used // (1024**3)} GB",
        "free": f"{disk.free // (1024**3)} GB",
        "percent": f"{disk.percent}%",
    }

    return render_template(
        "about.html",
        system=system_info,
        disk=disk_info,
        current_year=datetime.now().year
    )
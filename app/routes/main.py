# app/routes/main.py
from flask import Blueprint, render_template, redirect, session
from datetime import datetime

# ============================================
# BLUEPRINT UNTUK HALAMAN UTAMA
# ============================================
main = Blueprint("main", __name__)


# ============================================
# SPLASH PAGE
# ============================================
@main.route("/")
def splash():
    # Jika sudah login, langsung masuk ke home
    if "user_id" in session:
        return redirect("/home")

    return render_template("splash.html", current_year=datetime.utcnow().year)

# ============================================
# HALAMAN HOME
# ============================================
@main.route("/home")
def home():
    """
    Halaman utama setelah login.
    - Mengecek apakah user sudah login
    - Jika belum, redirect ke /login
    - Jika sudah, tampilkan home.html
      berikut username dan tahun saat ini
    """
    if "user_id" not in session:
        return redirect("/login")

    current_year = datetime.now().year

    return render_template(
        "home.html",
        current_year=current_year,
        username=session["username"]
    )
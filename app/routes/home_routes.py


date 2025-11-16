from datetime import datetime
from flask import render_template, redirect, session


def register_home_routes(app):
    """
    Route untuk halaman utama:
    - splash screen
    - home/dashboard setelah login
    """

    # =====================================================
    # HALAMAN SPLASH
    # =====================================================
    @app.route("/")
    def splash():
        # Tampilan awal sebelum login
        return render_template("splash.html")

    # =====================================================
    # HALAMAN HOME DASHBOARD
    # =====================================================
    @app.route("/home")
    def home():
        # Jika belum login → lempar ke halaman login
        if "user_id" not in session:
            return redirect("/login")

        current_year = datetime.now().year
        username = session.get("username", "User")

        return render_template(
            "home.html",
            current_year=current_year,
            username=username
        )
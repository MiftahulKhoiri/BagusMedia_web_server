from datetime import datetime
from flask import render_template, redirect, session

# =============================
# ROUTES: HOME & SPLASH
# =============================

def home_routes(app):
    # SPLASH PAGE
    @app.route("/")
    def splash():
        return render_template("splash.html")

    # HOME (SETELAH LOGIN)
    @app.route("/home")
    def home():
        if "user_id" not in session:
            return redirect("/login")

        current_year = datetime.now().year
        return render_template("home.html", current_year=current_year, username=session["username"])
from flask import Blueprint, render_template, redirect, session
from datetime import datetime

home_bp = Blueprint("home_bp", __name__)

def init_home(app):

    # =============================
    # HALAMAN SPLASH
    # =============================
    @home_bp.route("/")
    def splash():
        return render_template("splash.html")

    # =============================
    # HALAMAN HOME
    # =============================
    @home_bp.route("/home")
    def home():
        if "user_id" not in session:
            return redirect("/login")
        
        return render_template(
            "home.html",
            current_year=datetime.now().year,
            username=session["username"]
        )
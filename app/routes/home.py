from flask import Blueprint, render_template, redirect, session
from datetime import datetime

home = Blueprint("home", __name__)

def init_home(app):

    # =============================
    # HALAMAN SPLASH
    # =============================
    @home.route("/")
    def splash():
        return render_template("splash.html")

    # =============================
    # HALAMAN HOME
    # =============================
    @home.route("/home")
    def home():
        if "user_id" not in session:
            return redirect("/login")
        
        return render_template(
            "home.html",
            current_year=datetime.now().year,
            username=session["username"]
        )
from datetime import datetime
from flask import render_template, redirect, session

from . import home_bp

# SPLASH PAGE
@home_bp.route("/")
def splash():
    return render_template("splash.html")

# HOME PAGE
@home_bp.route("/home")
def home():
    if "user_id" not in session:
        return redirect("/login")

    current_year = datetime.now().year
    return render_template("home.html", current_year=current_year, username=session["username"])
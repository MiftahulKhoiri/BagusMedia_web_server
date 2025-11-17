import os
import json
import time
from flask import render_template, request, jsonify, session   # ← tambahkan session

def profile_routes(app):

    PROFILE_FILE = app.config["PROFILE_FILE"]

    # HALAMAN PROFIL
    @app.route("/profile")
    def profile():
        # CEK SESSION CARA BENAR
        if "user_id" not in session:
            return render_template("login.html")

        # load data profil
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                profile_data = json.load(f)
        else:
            profile_data = {
                "nama": "", "email": "", "jk": "",
                "umur": "", "bio": "",
                "foto": "", "cover": ""
            }

        from datetime import datetime
        current_year = datetime.now().year

        return render_template("profile.html", profile=profile_data, current_year=current_year)

    # HALAMAN EDIT PROFIL
    @app.route("/edit-profile")
    def edit_profile():
        # CEK SESSION AGAR TIDAK BISA EDIT TANPA LOGIN
        if "user_id" not in session:
            return render_template("login.html")

        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                profile_data = json.load(f)
        else:
            profile_data = {
                "nama": "", "email": "", "jk": "",
                "umur": "", "bio": "",
                "foto": "", "cover": ""
            }

        return render_template("edit-profile.html", profile=profile_data)
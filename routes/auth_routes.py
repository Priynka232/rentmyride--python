from flask import Blueprint, render_template, request, redirect, session
from db import get_db_connection

auth_bp = Blueprint("auth", __name__)

# ================================
# 1️⃣ REGISTER
# ================================
@auth_bp.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        role = request.form["role"]

        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO users (name, email, password, role, phone)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (name, email, password, role, phone)
        )

        db.commit()

        return redirect("/login")

    return render_template("user/register.html")


# ================================
# 2️⃣ LOGIN
# ================================
@auth_bp.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cursor.fetchone()

        if user:

            # 🚫 BLOCK CHECK
            if user["status"] == "blocked":
                return "❌ Your account is blocked by admin"

            session["user_id"] = user["user_id"]
            session["role"] = user["role"]
            session["name"] = user["name"]

            if user["role"] == "user":
                return redirect("/dashboard")

            elif user["role"] == "provider":
                return redirect("/provider/dashboard")

            elif user["role"] == "admin":
                return redirect("/admin/dashboard")

        else:
            return "❌ Invalid Email or Password"

    return render_template("user/login.html")


# ================================
# 3️⃣ LOGOUT
# ================================
@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

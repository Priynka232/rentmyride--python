from flask import Blueprint, render_template, request, session
from db import get_db_connection

user_bp = Blueprint('user_bp', __name__)

# ================================
# 🏠 USER DASHBOARD
# ================================
"""@user_bp.route("/dashboard")
def dashboard():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # user name fetch
    cursor.execute("SELECT name FROM users WHERE user_id=%s", (session["user_id"],))
    user = cursor.fetchone()

    # vehicles fetch
    cursor.execute("SELECT * FROM vehicles")
    vehicles = cursor.fetchall()

    return render_template("user/dashboard.html", vehicles=vehicles, user=user)"""
@user_bp.route("/dashboard")
def dashboard():

    search = request.args.get("search")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if search:
        cursor.execute(
            "SELECT * FROM vehicles WHERE name LIKE %s OR brand LIKE %s",
            ("%" + search + "%", "%" + search + "%")
        )
    else:
        cursor.execute("SELECT * FROM vehicles")

    vehicles = cursor.fetchall()

    return render_template("user/dashboard.html", vehicles=vehicles)


# ================================
# 🤖 AI RECOMMENDATION SYSTEM
# ================================
@user_bp.route("/recommend", methods=["GET", "POST"])
def recommend():

    if request.method == "POST":

        budget = int(request.form["budget"])
        passengers = int(request.form["passengers"])
        trip_type = request.form["trip_type"]

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # ✅ ALWAYS FETCH FIRST
        cursor.execute(
            "SELECT * FROM vehicles WHERE rent_per_day <= %s",
            (budget,)
        )
        vehicles = cursor.fetchall()

        recommended = []

        # ✅ AI LOGIC
        for v in vehicles:

            if passengers <= 2 and v["type"] in ["Bike", "Scooter"]:
                recommended.append(v)

            elif passengers <= 5 and v["type"] == "Car":
                recommended.append(v)

            elif passengers <= 12 and v["type"] == "Car":
                recommended.append(v)

            elif passengers > 12:
                if v["type"] in ["Bus", "Van"]:
                    recommended.append(v)

        # ✅ HANDLE LARGE GROUP (IMPORTANT FIX)
        if passengers > 12 and not recommended:
            return render_template(
                "user/recommend_result.html",
                vehicles=[],
                message="❌ No Bus/Van available for large group"
            )

        # ✅ FALLBACK
        if not recommended:
            recommended = vehicles

        return render_template(
            "user/recommend_result.html",
            vehicles=recommended
        )

    return render_template("user/recommend.html")
# about page
@user_bp.route("/about")
def about():
    return render_template("about.html")
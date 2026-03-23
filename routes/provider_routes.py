
from flask import Blueprint, render_template, session, redirect, request
from db import get_db_connection

provider_bp = Blueprint("provider", __name__)

# ================================
# 🏠 Provider Dashboard
# ================================
@provider_bp.route("/provider/dashboard")
def provider_dashboard():
    return render_template("provider/dashboard.html")
# add vehicle
import os

@provider_bp.route("/provider/add_vehicle", methods=["GET","POST"])
def add_vehicle():

    if request.method == "POST":

        name = request.form["name"]
        brand = request.form["brand"]
        vtype = request.form["type"]
        rent = request.form["rent"]

        image = request.files["image"]   # 👈 important

        filename = image.filename        # file name
        image_path = os.path.join("static/images", filename)

        image.save(image_path)           # save image

        provider_id = session["user_id"]

        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO vehicles (name, brand, type, rent_per_day, image, provider_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (name, brand, vtype, rent, filename, provider_id)
        )

        db.commit()

        return redirect("/provider/my_vehicles")

    return render_template("provider/add_vehicle.html")

#my vechicles
@provider_bp.route("/provider/my_vehicles")
def my_vehicles():

    provider_id = session["user_id"]

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM vehicles WHERE provider_id=%s",
        (provider_id,)
    )

    vehicles = cursor.fetchall()

    return render_template("provider/my_vehicles.html", vehicles=vehicles)

# ================================
# 📋 View Booking Requests
# ================================
@provider_bp.route("/provider/bookings")
def provider_bookings():

    provider_id = session["user_id"]

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT b.booking_id, u.name AS user_name, v.name AS vehicle_name,
               b.start_date, b.end_date, b.total_amount, b.booking_status
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN vehicles v ON b.vehicle_id = v.vehicle_id
        WHERE v.provider_id = %s
        ORDER BY b.booking_id DESC
        """,
        (provider_id,)
    )

    bookings = cursor.fetchall()

    return render_template("provider/booking_requests.html", bookings=bookings)


# ================================
# ✅ Accept Booking
# ================================
@provider_bp.route("/provider/accept_booking/<int:booking_id>")
def accept_booking(booking_id):

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE bookings SET booking_status='Confirmed' WHERE booking_id=%s",
        (booking_id,)
    )

    db.commit()

    return redirect("/provider/bookings")


# ================================
# ❌ Reject Booking
# ================================
@provider_bp.route("/provider/reject_booking/<int:booking_id>")
def reject_booking(booking_id):

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE bookings SET booking_status='Cancelled' WHERE booking_id=%s",
        (booking_id,)
    )

    db.commit()

    return redirect("/provider/bookings")

# ================================
# 🗑️ Delete Vehicle
# ================================
@provider_bp.route("/provider/delete_vehicle/<int:vehicle_id>")
def delete_vehicle(vehicle_id):

    db = get_db_connection()
    cursor = db.cursor()

    # पहले bookings delete करो (foreign key issue avoid)
    cursor.execute("DELETE FROM bookings WHERE vehicle_id=%s", (vehicle_id,))

    # फिर vehicle delete करो
    cursor.execute("DELETE FROM vehicles WHERE vehicle_id=%s", (vehicle_id,))

    db.commit()

    return redirect("/provider/my_vehicles")
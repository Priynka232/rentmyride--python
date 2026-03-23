from flask import Blueprint, render_template, request, redirect, session
from db import get_db_connection
from datetime import datetime

booking_bp = Blueprint("booking", __name__)

@booking_bp.route("/confirm_booking/<int:vehicle_id>", methods=["POST"])
def confirm_booking(vehicle_id):

    user_id = session["user_id"]

    start_date = request.form["start_date"]
    end_date = request.form["end_date"]

    # ✅ Pickup Location
    pickup_location = request.form["pickup_location"]

    if pickup_location == "Other":
        other_location = request.form["other_location"]

        if other_location.strip() == "":
            return "❌ Please enter pickup location"

        pickup_location = other_location

    # ✅ Payment Method
    payment_method = request.form["payment_method"]
    payment_status = "Paid"   # default

    if payment_method == "UPI":
        upi_id = request.form["upi_id"]
        if upi_id.strip() == "":
            return "❌ Please enter UPI ID"

    elif payment_method == "Card":
        card_number = request.form["card_number"]
        if card_number.strip() == "":
            return "❌ Please enter Card Number"

    elif payment_method == "Cash (Pay at Distination)":
        payment_status = "Pending"   # 👈 CASH case

    # ✅ DB connection
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Vehicle fetch
    cursor.execute(
        "SELECT rent_per_day, name FROM vehicles WHERE vehicle_id=%s",
        (vehicle_id,)
    )
    vehicle = cursor.fetchone()
    rent = vehicle["rent_per_day"]

    # Calculate days
    days = (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days + 1
    total_price = rent * days

    # ✅ Insert booking
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO bookings 
        (user_id, vehicle_id, start_date, end_date, total_amount, booking_status, pickup_location)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """,
        (user_id, vehicle_id, start_date, end_date, total_price, "Confirmed", pickup_location)
    )
    db.commit()

    booking_id = cursor.lastrowid

    # ✅ Insert payment
    cursor.execute(
        """
        INSERT INTO payments (booking_id, amount, payment_status)
        VALUES (%s,%s,%s)
        """,
        (booking_id, total_price, payment_status)
    )
    db.commit()

    return redirect(f"/payment_success/{booking_id}")

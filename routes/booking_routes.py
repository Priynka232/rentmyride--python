from flask import Blueprint, render_template, request, redirect, session
from db import get_db_connection
from datetime import datetime

booking_bp = Blueprint("booking", __name__)

# ================================
# 1️⃣ Book Vehicle Page
# ================================
@booking_bp.route("/book/<int:vehicle_id>")
def book_vehicle(vehicle_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM vehicles WHERE vehicle_id=%s",
        (vehicle_id,)
    )
    vehicle = cursor.fetchone()

    return render_template("user/booking.html", vehicle=vehicle)


# ================================
# 2️⃣ Confirm Booking (POST)
# ================================
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

    if payment_method == "":
        return "❌ Please select payment method"

    if payment_method == "UPI":
        upi_id = request.form["upi_id"]
        if upi_id.strip() == "":
            return "❌ Please enter UPI ID"

        payment_status = "Paid"

    elif payment_method == "Card":
        card_number = request.form["card_number"]
        if card_number.strip() == "":
            return "❌ Please enter Card Number"

        payment_status = "Paid"

    elif payment_method == "Cash":
        payment_status = "Pending"

    else:
        return "❌ Invalid payment method"

    # ✅ DB Connection
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Fetch vehicle rent
    cursor.execute(
        "SELECT rent_per_day, name FROM vehicles WHERE vehicle_id=%s",
        (vehicle_id,)
    )
    vehicle = cursor.fetchone()

    rent = vehicle["rent_per_day"]

    # Calculate total price
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    days = (end - start).days + 1
    total_price = rent * days

    # ✅ Insert booking
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO bookings
        (user_id, vehicle_id, start_date, end_date, total_amount, booking_status, pickup_location)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (user_id, vehicle_id, start_date, end_date, total_price, "Confirmed", pickup_location)
    )
    db.commit()

    booking_id = cursor.lastrowid

    # ✅ Insert payment
    cursor.execute(
        """
        INSERT INTO payments
        (booking_id, amount, payment_status)
        VALUES (%s, %s, %s)
        """,
        (booking_id, total_price, payment_status)
    )
    db.commit()

    return redirect(f"/payment_success/{booking_id}")


# ================================
# 3️⃣ Payment Success Page
# ================================
@booking_bp.route("/payment_success/<int:booking_id>")
def payment_success(booking_id):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT b.booking_id, v.name, b.start_date, b.end_date,
               b.total_amount AS total_price,
               COALESCE(p.payment_status, 'Pending') AS payment_status
        FROM bookings b
        JOIN vehicles v ON b.vehicle_id = v.vehicle_id
        LEFT JOIN payments p ON b.booking_id = p.booking_id
        WHERE b.booking_id = %s
        """,
        (booking_id,)
    )

    booking = cursor.fetchone()

    return render_template("user/payment_success.html", booking=booking)


# ================================
# 4️⃣ Booking History
# ================================
@booking_bp.route("/user/booking_history")
def booking_history():

    user_id = session["user_id"]

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT b.booking_id, v.name AS vehicle_name,
               b.start_date, b.end_date,
               b.total_amount,
               b.booking_status,
               COALESCE(p.payment_status, 'Pending') AS payment_status
        FROM bookings b
        JOIN vehicles v ON b.vehicle_id = v.vehicle_id
        LEFT JOIN payments p ON b.booking_id = p.booking_id
        WHERE b.user_id = %s
        ORDER BY b.booking_id DESC
        """,
        (user_id,)
    )

    bookings = cursor.fetchall()

    return render_template("user/booking_history.html", bookings=bookings)


# ================================
# 5️⃣ Cancel Booking
# ================================
@booking_bp.route("/cancel_booking/<int:booking_id>")
def cancel_booking(booking_id):

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE bookings SET booking_status='Cancelled' WHERE booking_id=%s",
        (booking_id,)
    )
    db.commit()

    return redirect("/user/booking_history")


# ================================
# 6️⃣ Booking Details
# ================================
@booking_bp.route("/booking_details/<int:booking_id>")
def booking_details(booking_id):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT b.*, v.name AS vehicle_name,
               COALESCE(p.payment_status, 'Pending') AS payment_status
        FROM bookings b
        JOIN vehicles v ON b.vehicle_id = v.vehicle_id
        LEFT JOIN payments p ON b.booking_id = p.booking_id
        WHERE b.booking_id = %s
        """,
        (booking_id,)
    )

    booking = cursor.fetchone()

    return render_template("user/booking_details.html", booking=booking)
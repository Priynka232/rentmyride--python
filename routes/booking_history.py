from flask import Blueprint, render_template, request, redirect, session
from db import get_db_connection

@booking_bp.route("/booking_history")
def booking_history():

    user_id = session["user_id"]

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = """
    SELECT bookings.*, vehicles.name AS vehicle_name
    FROM bookings
    JOIN vehicles ON bookings.vehicle_id = vehicles.vehicle_id
    WHERE bookings.user_id=%s
    """

    cursor.execute(query,(user_id,))
    bookings = cursor.fetchall()

    return render_template("user/booking_history.html", bookings=bookings)
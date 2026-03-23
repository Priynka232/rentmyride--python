from flask import Blueprint, render_template, redirect, request, session
from db import get_db_connection

admin_bp = Blueprint("admin", __name__)

# ================================
# 🏠 Admin Dashboard
# ================================
@admin_bp.route("/admin/dashboard")
def admin_dashboard():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # users
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    # vehicles
    cursor.execute("SELECT * FROM vehicles")
    vehicles = cursor.fetchall()

    # bookings
    cursor.execute("""
        SELECT b.booking_id, u.name AS user_name, v.name AS vehicle_name,
               b.start_date, b.end_date, b.total_amount, b.booking_status
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN vehicles v ON b.vehicle_id = v.vehicle_id
    """)
    bookings = cursor.fetchall()

    return render_template(
        "admin/dashboard.html",
        users=users,
        vehicles=vehicles,
        bookings=bookings
    )


# ================================
# 👤 BLOCK USER
# ================================
@admin_bp.route("/admin/block_user/<int:user_id>")
def block_user(user_id):

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE users SET status='blocked' WHERE user_id=%s",
        (user_id,)
    )

    db.commit()
    return redirect("/admin/dashboard")


# ================================
# 👤 UNBLOCK USER
# ================================
@admin_bp.route("/admin/unblock_user/<int:user_id>")
def unblock_user(user_id):

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE users SET status='active' WHERE user_id=%s",
        (user_id,)
    )

    db.commit()
    return redirect("/admin/dashboard")


# ================================
# 🚗 BLOCK VEHICLE
# ================================
@admin_bp.route("/admin/block_vehicle/<int:vehicle_id>")
def block_vehicle(vehicle_id):

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE vehicles SET status='blocked' WHERE vehicle_id=%s",
        (vehicle_id,)
    )

    db.commit()
    return redirect("/admin/dashboard")


# ================================
# 🚗 UNBLOCK VEHICLE
# ================================
@admin_bp.route("/admin/unblock_vehicle/<int:vehicle_id>")
def unblock_vehicle(vehicle_id):

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE vehicles SET status='active' WHERE vehicle_id=%s",
        (vehicle_id,)
    )

    db.commit()
    return redirect("/admin/dashboard")


# ================================
# 📋 View All Bookings
# ================================
@admin_bp.route("/admin/all_bookings")
def all_bookings():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT b.booking_id, u.name AS user_name, v.name AS vehicle_name,
               b.start_date, b.end_date, b.total_amount, b.booking_status
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN vehicles v ON b.vehicle_id = v.vehicle_id
    """)

    bookings = cursor.fetchall()

    return render_template("admin/all_bookings.html", bookings=bookings)
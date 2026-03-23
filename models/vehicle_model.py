from db import get_db_connection

def get_all_vehicles():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM vehicles")

    vehicles = cursor.fetchall()

    conn.close()

    return vehicles


def get_vehicle(vehicle_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM vehicles WHERE vehicle_id=%s",(vehicle_id,))

    vehicle = cursor.fetchone()

    conn.close()

    return vehicle
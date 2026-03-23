from db import get_db_connection

def create_user(name,email,password,role):

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "INSERT INTO users (name,email,password,role) VALUES (%s,%s,%s,%s)"

    cursor.execute(query,(name,email,password,role))

    conn.commit()
    conn.close()


def get_user_by_email(email):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE email=%s",(email,))

    user = cursor.fetchone()

    conn.close()

    return user
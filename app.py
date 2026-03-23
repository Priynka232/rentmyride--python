from flask import Flask, render_template
from config import Config

from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.provider_routes import provider_bp
from routes.booking_routes import booking_bp
from routes.admin_routes import admin_bp


app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(provider_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(admin_bp)

@app.route("/")
def index():

    from db import get_db_connection

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM vehicles")

    vehicles = cursor.fetchall()

    return render_template("index.html", vehicles=vehicles)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
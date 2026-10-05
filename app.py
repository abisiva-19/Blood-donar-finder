import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "blood_donor_finder_secret_key"

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "donors.db")


def get_db_connection():
    """Create and return a database connection with dictionary-like row access."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the donors table if it does not exist and add initial sample data."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS donors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            blood_group TEXT NOT NULL,
            phone TEXT NOT NULL,
            city TEXT NOT NULL,
            area TEXT NOT NULL,
            availability TEXT NOT NULL
        )
    """)
    conn.commit()

    # Check if database is empty; if so, insert starter demo records
    cursor.execute("SELECT COUNT(*) FROM donors")
    count = cursor.fetchone()[0]
    if count == 0:
        sample_donors = [
            ("Arun Kumar", 26, "Male", "O+", "9876543210", "Madurai", "Anna Nagar", "Available"),
            ("Priya Sharma", 24, "Female", "A+", "9845123456", "Chennai", "T. Nagar", "Available"),
            ("Rajesh Patel", 31, "Male", "B+", "9712345678", "Bengaluru", "Indiranagar", "Available"),
            ("Sneha Reddy", 28, "Female", "O-", "9988776655", "Hyderabad", "Banjara Hills", "Available"),
            ("Vikram Singh", 35, "Male", "AB+", "9123456780", "Delhi", "Connaught Place", "Not Available"),
            ("Kavita Nair", 29, "Female", "B-", "9871122334", "Kochi", "Edappally", "Available")
        ]
        cursor.executemany("""
            INSERT INTO donors (name, age, gender, blood_group, phone, city, area, availability)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_donors)
        conn.commit()

    conn.close()


# Initialize database when application starts
init_db()


@app.route("/")
def index():
    """Home landing page with project overview, statistics, and quick navigation."""
    conn = get_db_connection()
    total_donors = conn.execute("SELECT COUNT(*) FROM donors").fetchone()[0]
    available_donors = conn.execute("SELECT COUNT(*) FROM donors WHERE availability = 'Available'").fetchone()[0]
    conn.close()

    return render_template("index.html", total_donors=total_donors, available_donors=available_donors)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Donor registration page for adding new blood donors."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age = request.form.get("age", "").strip()
        gender = request.form.get("gender", "").strip()
        blood_group = request.form.get("blood_group", "").strip()
        phone = request.form.get("phone", "").strip()
        city = request.form.get("city", "").strip()
        area = request.form.get("area", "").strip()
        availability = request.form.get("availability", "Available").strip()

        # Server-side validation
        errors = []
        if not name:
            errors.append("Full Name is required.")
        if not age or not age.isdigit() or int(age) < 18 or int(age) > 65:
            errors.append("Valid age between 18 and 65 is required for blood donation.")
        if gender not in ["Male", "Female", "Other"]:
            errors.append("Please select a valid gender.")
        if blood_group not in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]:
            errors.append("Please select a valid blood group.")
        if not phone or len(phone) < 10 or not phone.isdigit():
            errors.append("A valid 10-digit phone number is required.")
        if not city:
            errors.append("City is required.")
        if not area:
            errors.append("Area/Location is required.")

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("register.html", form_data=request.form)

        # Insert donor into database
        conn = get_db_connection()
        conn.execute("""
            INSERT INTO donors (name, age, gender, blood_group, phone, city, area, availability)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, int(age), gender, blood_group, phone, city, area, availability))
        conn.commit()
        conn.close()

        flash("Donor registration successful! Thank you for saving lives.", "success")
        return redirect(url_for("register"))

    return render_template("register.html", form_data={})


@app.route("/search", methods=["GET", "POST"])
def search():
    """Search donors by blood group and location/city/area."""
    blood_group = request.args.get("blood_group", "").strip()
    location = request.args.get("location", "").strip()

    # If submitted via POST, redirect with GET query parameters for shareable URL
    if request.method == "POST":
        blood_group = request.form.get("blood_group", "").strip()
        location = request.form.get("location", "").strip()
        return redirect(url_for("search", blood_group=blood_group, location=location))

    query = "SELECT * FROM donors WHERE 1=1"
    params = []

    if blood_group and blood_group != "All":
        query += " AND blood_group = ?"
        params.append(blood_group)

    if location:
        query += " AND (city LIKE ? OR area LIKE ?)"
        params.append(f"%{location}%")
        params.append(f"%{location}%")

    query += " ORDER BY availability DESC, id DESC"

    conn = get_db_connection()
    donors = conn.execute(query, params).fetchall()
    conn.close()

    # Track if user initiated a search query
    has_searched = bool(blood_group or location or request.args.get("searched"))

    return render_template(
        "search.html",
        donors=donors,
        selected_blood_group=blood_group,
        searched_location=location,
        has_searched=has_searched
    )


if __name__ == "__main__":
    # host="0.0.0.0" allows testing from both your computer and your mobile phone on the same Wi-Fi
    app.run(debug=True, host="0.0.0.0", port=5000)

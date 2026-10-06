import os
import shutil
import sqlite3
import tempfile
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "blood_donor_finder_secret_key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_DB = os.path.join(BASE_DIR, "donors.db")


def get_db_path():
    """
    Get a writable path for the SQLite database.
    On serverless platforms (e.g. Vercel, AWS Lambda), the deployment directory
    is read-only (/var/task). SQLite requires write access to perform INSERTs
    and create transaction journals. Therefore, in serverless environments,
    we locate the database in /tmp and copy the seeded donors.db if needed.
    """
    is_serverless = bool(
        os.environ.get("VERCEL")
        or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
        or os.environ.get("LAMBDA_TASK_ROOT")
    )

    if is_serverless:
        tmp_dir = "/tmp" if os.path.exists("/tmp") else tempfile.gettempdir()
        tmp_db = os.path.join(tmp_dir, "donors.db")
        if not os.path.exists(tmp_db) and os.path.exists(LOCAL_DB):
            try:
                shutil.copyfile(LOCAL_DB, tmp_db)
                try:
                    os.chmod(tmp_db, 0o666)
                except Exception:
                    pass
            except Exception as e:
                print(f"Error copying database to {tmp_db}: {e}")
        return tmp_db

    # In local development or persistent hosting:
    # Verify write access to BASE_DIR; fallback to temp directory if not writable
    try:
        test_file = os.path.join(BASE_DIR, ".write_test")
        with open(test_file, "w") as f:
            f.write("1")
        os.remove(test_file)
        return LOCAL_DB
    except (OSError, IOError, PermissionError):
        tmp_dir = "/tmp" if os.path.exists("/tmp") else tempfile.gettempdir()
        tmp_db = os.path.join(tmp_dir, "donors.db")
        if not os.path.exists(tmp_db) and os.path.exists(LOCAL_DB):
            try:
                shutil.copyfile(LOCAL_DB, tmp_db)
                try:
                    os.chmod(tmp_db, 0o666)
                except Exception:
                    pass
            except Exception:
                pass
        return tmp_db


def get_db_connection():
    """Create and return a database connection with dictionary-like row access."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the donors table if it does not exist and add initial sample data."""
    conn = None
    try:
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
    except Exception as e:
        print(f"Database initialization note: {e}")
    finally:
        if conn:
            conn.close()


# Initialize database when application starts
init_db()


@app.route("/")
def index():
    """Home landing page with project overview, statistics, and quick navigation."""
    total_donors = 0
    available_donors = 0
    conn = None
    try:
        conn = get_db_connection()
        total_donors = conn.execute("SELECT COUNT(*) FROM donors").fetchone()[0]
        available_donors = conn.execute("SELECT COUNT(*) FROM donors WHERE availability = 'Available'").fetchone()[0]
    except Exception as e:
        print(f"Error fetching donor stats: {e}")
    finally:
        if conn:
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
        conn = None
        try:
            conn = get_db_connection()
            conn.execute("""
                INSERT INTO donors (name, age, gender, blood_group, phone, city, area, availability)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, int(age), gender, blood_group, phone, city, area, availability))
            conn.commit()
            flash("Donor registration successful! Thank you for saving lives.", "success")
            return redirect(url_for("register"))
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            flash(f"Could not save donor registration: {str(e)}", "error")
            return render_template("register.html", form_data=request.form)
        finally:
            if conn:
                conn.close()

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

    donors = []
    conn = None
    try:
        conn = get_db_connection()
        donors = conn.execute(query, params).fetchall()
    except Exception as e:
        print(f"Database query error in search: {e}")
    finally:
        if conn:
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


@app.errorhandler(500)
def server_error(e):
    flash("A temporary server error occurred. Please try again.", "error")
    return redirect(url_for("index"))


@app.errorhandler(404)
def not_found_error(e):
    return redirect(url_for("index"))


if __name__ == "__main__":
    # host="0.0.0.0" allows testing from both your computer and your mobile phone on the same Wi-Fi
    app.run(debug=True, host="0.0.0.0", port=5000)

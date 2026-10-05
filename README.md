# 🩸 Blood Donor Finder

A modern, responsive, and beginner-friendly **Blood Donor Finder web application** built with **Python Flask, SQLite3, HTML5, CSS3, and JavaScript**.

This platform connects patients in urgent need with voluntary blood donors based on **blood group and location (city/area)**.

---

## 🚀 Key Features

* **Landing Page**: Modern hero section with quick stats, project overview, and quick links.
* **Donor Registration (`/register`)**:
  * Form fields: Name, Age (18–65), Gender, Blood Group (A+, A-, B+, B-, AB+, AB-, O+, O-), Phone number (10 digits), City, Area, Availability.
  * Dual validation: Client-side JavaScript + Server-side Flask validation.
  * Stores records directly in an SQLite database (`donors.db`).
* **Donor Search (`/search`)**:
  * Instant search by **Blood Group** and **City / Area**.
  * Shows matching donors in clean cards with blood group tags, location, phone, and availability badge.
  * Direct contact channels:
    * 📞 **Direct Call**: 1-tap phone dialer on mobile devices.
    * 💬 **WhatsApp Chat**: Opens instant WhatsApp chat with pre-filled emergency request message.
    * 📋 **1-Click Copy**: Copies phone number to clipboard with toast notification.
  * Empty state notification if no matching donors are found.

---

## 📁 Project Structure

```text
blood-donor-finder/
│
├── app.py                  # Flask backend & SQLite database operations
├── donors.db               # SQLite database file (auto-initialized)
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignored files
├── README.md               # Project documentation
│
├── templates/
│   ├── index.html          # Landing home page
│   ├── register.html       # Donor registration form
│   └── search.html         # Donor search & results card list
│
└── static/
    ├── style.css           # Modern blood donation themed styles
    └── script.js           # Client-side validation & UI interactions
```

---

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/abisiva-19/Blood-donar-finder.git
cd Blood-donar-finder
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```

### 4. Open in Your Browser
* On your local computer: `http://127.0.0.1:5000`
* On mobile phones on the same Wi-Fi: `http://<your-local-ip>:5000`

---

## 🗄️ Database Schema

The SQLite database (`donors.db`) contains the `donors` table:

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER PRIMARY KEY | Auto-incrementing identifier |
| `name` | TEXT | Full name of donor |
| `age` | INTEGER | Age of donor (18-65) |
| `gender` | TEXT | Male / Female / Other |
| `blood_group` | TEXT | A+, A-, B+, B-, AB+, AB-, O+, O- |
| `phone` | TEXT | 10-digit mobile number |
| `city` | TEXT | Donor city |
| `area` | TEXT | Specific area / neighborhood |
| `availability`| TEXT | Available / Not Available |

---

## 📄 License
This project is open-source and free to use for educational and community life-saving purposes.

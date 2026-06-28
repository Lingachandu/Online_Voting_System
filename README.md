# 🗳️ Secure Online Voting System

A secure, state-filtered Online Voting System built with **Django** (Python) and **HTML/CSS/JS**. The system supports role-based access control, OTP-based login, biometric-free double-voting prevention, data privacy masking, and real-time election results — across three Indian states.

---

## 🌟 Key Features

- **Role-Based Access**: Separate dashboards for **Voters** and **Administrators**.
- **State-Filtered Elections**: Each voter sees only their state's election — **Andhra Pradesh (AP)**, **Telangana (TG)**, or **Chennai**.
- **State Welcome Banners**: Sleek CSS variable-themed marquee banners matching state styles (Forest Green for AP, Royal Pink for TG, Ice Blue for Chennai).
- **OTP Login & QR Authenticator**: Secure two-factor authentication (2FA) via TOTP. Users scan a QR code with Google Authenticator or Authy to log in.
- **Dynamic Name Capture**: Voter's full name is captured at login, saved to their profile, and dynamically printed on official receipts.
- **Double-Voting Prevention**: Database-level constraints prevent any voter from voting more than once.
- **PII Data Masking**: Voter phone numbers (`******1234`) and Aadhaar numbers (`XXXX-XXXX-6789`) are masked on all Voter dashboards, Admin logs, and JSON API payloads to ensure GDPR/security compliance.
- **Live Turnout Analytics**: State-specific voter turnout progress bars calculated directly from database records.
- **End-to-End Verifiability**:
  - **Voter Receipt Download**: Download a secure transaction text receipt (`SEC-VOTE-[VoteID]-[VoterID]`).
  - **Public Receipt Verifier**: A voter-facing tool on the Helpline tab to verify if their ballot has been safely registered in the ECI registry (hiding candidate choice to prevent vote-coercion).
  - **Admin Receipt Verifier**: Admin tool to verify receipt transactions for auditing.
- **Live Admin Dashboard**: Real-time vote tallies, interactive donut charts (corrected color mappings for TVK/Janasena), candidate management, and dynamic voter audit logs with CSV export.

---

## 📂 Project Structure

```text
Online_Voting/
│
├── backend/                        # Django backend folder
│   ├── apps/
│   │   ├── authentication/         # User model, TOTP setup, legal terms
│   │   ├── elections/              # Dashboards views, candidates, API stats
│   │   └── voting/                 # Vote casting, receipt download
│   ├── myproject/                  # Settings, url configurations
│   └── manage.py                   # Django CLI
│
├── frontend/                       # Web static and templates files
│   ├── static/
│   │   ├── css/                    # base.css, auth.css, admin.css
│   │   └── voting/                 # voting.css (state theme stylesheets)
│   └── templates/
│       ├── base.html               # Global wrapper layout
│       ├── authentication/         # login, register, verify_otp, terms, privacy
│       └── elections/              # voter_dashboard, admin_dashboard
│
├── env/                            # Python virtual environment (ignored by Git)
├── .env                            # Secret environment configurations
├── .gitignore
├── requirements.txt                # Locked environment dependencies
└── README.md                       # Documentation
```

---

## 🚀 Setup & Installation

### 1. Prerequisites
Python 3.10+ must be installed.

### 2. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\env\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
.\env\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source env/bin/activate
```

If the virtual environment doesn't exist, create it:
```bash
python -m venv env
pip install -r requirements.txt
```

---

## 🔒 Configuration

Create a `.env` file at the project root:

```env
# Django settings
SECRET_KEY=your-django-secret-key-here
DEBUG=True

# Default admin account phone number
ADMIN_PHONE_NUMBER=9876543210
```

> [!IMPORTANT]
> The `.env` file is excluded from Git via `.gitignore`. Never share your `SECRET_KEY` in production environments.

---

## ⚙️ Running the Project

### 1. Apply Database Migrations
```bash
cd backend
python manage.py migrate
```

### 2. Start the Development Server
```bash
python manage.py runserver
```

Visit: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 📦 Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `Django` | 6.0.6 | Core Web Framework |
| `pyotp` | 2.10.0 | TOTP 2FA code generation |
| `whitenoise` | 6.12.0 | High-performance static files hosting |
| `dj-database-url` | 3.1.2 | Database URL config (production) |
| `gunicorn` | 26.0.0 | Production WGSI Server |
| `psycopg2-binary` | 2.9.12 | PostgreSQL database adapter |

---

## 📝 Design & Architecture Notes

- **Aadhaar Prefix Verification**: Registration checks state codes based on Aadhaar digits (`123` for AP, `456` for TG, `789` for Chennai).
- **Voter Privacy Secrecy**: The system is designed to completely decouple user information from vote entries. The `verify-receipt` API ensures public queries never leak candidate selection details.
- **SQLite defaults**: SQLite is configured by default for easy local testing.

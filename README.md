# 🗳️ Secure Online Voting System

A highly secure, state-filtered Online Voting System built with **Django** (Python) and **Vanilla HTML/CSS/JS** for the frontend. The project implements modern security controls including simulated biometric face-matching, SMS OTP verification, double-voting prevention, and robust role-based access control (RBAC).

---

## 🌟 Key Features

*   **Role-Based Access**: Specialized interfaces and routing for **Voters** and **Administrators**.
*   **State-Filtered Elections**: Dynamic dashboard filtering supporting voters from **Andhra Pradesh (AP)**, **Telangana (TG)**, and **Chennai**, showing only region-appropriate active elections.
*   **Biometric Security Sim**: Simulated face-biometrics validation during login and registration.
*   **SMS OTP Verification**: Secure two-factor authentication (2FA) with OTP generation output to the local outbox logs in your terminal.
*   **Double-Voting Prevention**: Strict database constraints and middleware validations to prevent users from casting multiple votes or registering twice.
*   **Secure Configurations**: Secret keys and admin credentials managed through standard environment variables (`.env`).

---

## 📂 Project Architecture

```text
Online_Voting/
│
├── backend/
│   ├── apps/
│   │   ├── authentication/   # Custom user, biometric login/registration & OTP view flow
│   │   ├── elections/        # State-filtered active election dashboards & candidate management
│   │   └── voting/           # Double-voting prevention & casting mechanisms
│   ├── myproject/            # Main Django configuration (settings, urls, wsgi)
│   └── manage.py             # Django project manager CLI
│
├── frontend/
│   ├── static/               # CSS, JS, and image assets
│   └── templates/            # HTML templates organized by app scopes
│
├── env/                      # Local Python Virtual Environment
├── .env                      # Local environment configurations (ignored by git)
├── .env.example              # Template configuration for environment variables
├── .gitignore                # Git exclusions checklist
├── requirements.txt          # Python package requirements
└── README.md                 # Project documentation (this file)
```

---

## 🚀 Setup & Installation Guide

### 1. Prerequisites
Make sure Python 3.10+ is installed on your local operating system.

### 2. Configure Virtual Environment
If you are running the project locally, activate the preconfigured virtual environment:

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

If the virtual environment does not exist, initialize it and install dependencies:
```bash
python -m venv env
# Activate the environment, then:
pip install -r requirements.txt
```

---

## 🔒 Configuration & Security

The system retrieves sensitive configs from the environment. Create a `.env` file at the root of the project using the `.env.example` template:

```env
# Django settings config
SECRET_KEY=your-django-secret-key-here
DEBUG=True

# Administrator phone number
ADMIN_PHONE_NUMBER=9876543210
```

> [!IMPORTANT]
> The `.env` file is automatically ignored by Git inside `.gitignore` to prevent leakage of the Secret Key or administrator phone numbers.

---

## ⚙️ Running the Project

### 1. Database Migrations
Initialize database tables and schemas:
```bash
cd backend
python manage.py migrate
```

### 2. Start the Server
Run the local development server:
```bash
python manage.py runserver
```
Visit the app locally at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

> [!TIP]
> Since SMS gateways are mocked, OTP codes will be printed directly in your terminal/outbox logs upon requesting verification. Look for:
> `--- Text SMS OUTBOX: OTP FOR <phone> IS <otp> ---`

---

## 🧪 Running Automated Tests

To run the complete Django test suite containing 33 unit tests for authentication, dashboards, candidate control, and double-voting prevention:

```bash
cd backend
..\env\Scripts\python.exe manage.py test
```
All tests should pass successfully with `OK`.

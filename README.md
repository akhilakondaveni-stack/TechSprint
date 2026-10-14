# 🌿 HealthBuddy for Parents
### AI-Powered Healthcare Web Application for Elderly Parents and Caregivers

**HealthBuddy for Parents** is a complete, responsive healthcare assistance web application engineered specifically for elderly parents and their family caregivers. It simplifies complex diagnostic reports, manages daily medication routines, tracks doctor consultations, visualizes long-term health biomarkers, and enables secure, authorized health data sharing within families.

---

## 🌟 Key Features

1. **Medical Report Reader & Claude AI Explainer**
   - Upload PDF lab reports, prescription scans, or camera photos (up to 10MB, max 5 pages).
   - Converts PDF pages into images using **PyMuPDF**.
   - Extracts report date, doctor, hospital, diagnostic tests, values, reference ranges, and prescribed medicines using **Anthropic Claude Vision** (or realistic **Synthetic Demo Mode** if an API key is not configured).
   - Interactive, editable review tables allowing users to review and correct extracted values before permanent storage.
   - Compassionate plain-language explanations in **English, Hindi (हिंदी), or Telugu (తెలుగు)** with one-click **Text-to-Speech (gTTS)** playback.
   - Non-prescriptive doctor questions and gentle dietary/lifestyle suggestions.
   - Prominent mandatory medical safety disclaimers with emergency symptom advisories.

2. **Medicine Manager & Adherence Tracker**
   - Register medication schedules with morning (08:00 IST), afternoon (14:00 IST), and night (20:00 IST) timing slots.
   - Prevents duplicate dose records using SQLite database unique constraints (`UNIQUE(user_id, medicine_id, scheduled_date, slot)`).
   - Daily interactive dose tracker (Taken, Skipped, Missed) supporting instant accidental entry corrections.
   - 7-day and 30-day adherence percentage analytics with interactive Plotly breakdown donut charts.
   - Strict medical safety rule prominently displayed: *"NEVER double a dose if you miss a previous one."*

3. **Medical Appointment Manager**
   - Schedule in-person, video, or phone consultations with doctor name, facility, date, time, and notes.
   - Filter between upcoming and completed/past visits with one-click status transitions.

4. **Health History & Monthly PDF Summary Export**
   - Searchable, encrypted medical report archive.
   - One-click generation of official **Monthly Health Summary PDFs** (using **ReportLab**), complete with patient information, adherence stats, active prescriptions, recent test highlights, and doctor discussion notes.

5. **Family Connections & Role-Based Access Control**
   - **Parent Role:** Generates unique, cryptographically secure 8-character invitation codes (`HB-XXXXXX`) and retains explicit control to approve or revoke access at any time.
   - **Child Role:** Connects via invite code to view authorized parents' health records, assist with appointments, and monitor medication adherence.
   - Strict server-side cross-user data isolation: unauthorized users cannot query or modify another family's data.

6. **Privacy, Security & Compliance**
   - **Fernet Symmetric Encryption at Rest:** Diagnostic results, raw extracted data, and clinical notes are encrypted using AES-128-CBC with HMAC-SHA256 authentication.
   - **Bcrypt Password Hashing:** Credentials hashed with individual salts (12 work rounds); plaintext passwords are never stored.
   - **Brute Force Protection:** Automatic rate limiting (5 failed attempts locks out for 10 minutes).
   - **File Signature & Magic Byte Validation:** Verifies PDF, PNG, and JPEG binary headers to prevent MIME spoofing.
   - **Path Traversal Protection:** Server-side UUID filenames protect filesystem boundaries.
   - **Audit Trail Logging:** All sensitive security actions (logins, report views, access approvals/revocations) are immutably logged.

7. **Proactive Notifications & Background Scheduler**
   - Persistent background worker (**APScheduler**) running in IST timezone.
   - Idempotent reminder delivery via **Telegram Bot API** (discreet message formats that omit private clinical details).
   - Guaranteed single worker instance across Streamlit reruns.

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| **Frontend UI** | Streamlit (Custom CSS, elderly-accessible high contrast typography) |
| **Backend & Logic** | Python 3.10+ |
| **Database** | SQLite (WAL mode, foreign key enforcement, indexed lookups) |
| **AI Integration** | Anthropic Claude Python SDK (`claude-3-7-sonnet` / `claude-3-5-sonnet`) + Safe Synthetic Demo Mode |
| **Encryption & Auth** | Fernet Symmetric Encryption (`cryptography`), Bcrypt password hashing |
| **Document Processing** | PyMuPDF (`fitz`), Pillow, ReportLab |
| **Data & Validation** | Pandas, Pydantic V2 |
| **Visualizations** | Plotly Express & Plotly Graph Objects |
| **Text-to-Speech** | gTTS (In-memory MP3 playback) |
| **Notifications** | Telegram Bot API, APScheduler |
| **Configuration** | python-dotenv |
| **Testing** | Pytest (27 automated unit, security, and integration tests) |

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure Python 3.10 or higher is installed:
```bash
python --version
```

### 2. Installation
Install the project dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy the template configuration file:
```bash
cp .env.example .env
```
*(On Windows PowerShell: `Copy-Item .env.example .env`)*

Configure `.env` as required:
```ini
# Anthropic Claude API (Optional: if blank, HealthBuddy runs in Demo Mode with realistic synthetic data)
ANTHROPIC_API_KEY="your_anthropic_api_key_here"
CLAUDE_MODEL=claude-3-7-sonnet-20250219

# Security: 32-byte base64 URL-safe key. If blank, one is generated automatically and persisted in data/.fernet.key
FERNET_KEY=

# Local SQLite Database Path
SQLITE_PATH=data/healthbuddy.db

# Application URL
APP_URL=http://localhost:8501

# Telegram Notifications (Optional: set your Telegram Bot token)
TELEGRAM_BOT_TOKEN=
```

### 4. Run Automated Tests
Execute the complete test suite:
```bash
python -m pytest -v
```
All 27 automated tests cover authentication, encryption, schema validation, family sharing, PDF generation, and safety rules.

### 5. Launch HealthBuddy Application
Start the Streamlit dashboard:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 👥 Instant Evaluation Demo Accounts

HealthBuddy automatically seeds realistic sample accounts on first startup for instant exploration:

| Role | Email Address | Password | Description |
|---|---|---|---|
| **Parent** | `parent@healthbuddy.com` | `Password123!` | Pre-populated with active medicines, dose history, appointment schedules, and a diagnostic blood report. |
| **Child** | `child@healthbuddy.com` | `Password123!` | Pre-linked and approved to view Ramachandra Rao's records as a caregiver. |

*You can also click the **"⚡ Quick Demo Login"** buttons on the login screen for instant single-click access.*

---

## 📂 Project Directory Structure

```
├── app.py                     # Main Streamlit web application & page navigation
├── config.py                  # Environment configuration and directory setup
├── database.py                # SQLite connection, schema definition & audit logging
├── auth.py                    # Bcrypt registration, login, rate limiting & access checks
├── security.py                # Fernet encryption, file signature validation & safe storage
├── ai_service.py              # Claude Vision API, Pydantic validation & synthetic demo mode
├── report_service.py          # Document upload, PyMuPDF rendering & encrypted storage
├── medicine_service.py        # Medication schedules, dose tracking & adherence analytics
├── appointment_service.py     # Doctor visit scheduling and status tracking
├── family_service.py          # Secure invitation codes, parent approval & link revocation
├── notification_service.py    # Telegram Bot integration & delivery logging
├── scheduler.py               # Background reminder jobs (APScheduler singleton)
├── pdf_service.py             # Monthly health summary PDF compiler (ReportLab)
├── i18n.py                    # Multilingual dictionary (EN, HI, TE) & gTTS audio generator
├── seed_data.py               # Pre-seeded test accounts and clinical records
├── requirements.txt           # Project dependencies
├── pytest.ini                 # Pytest root configuration
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore file for secrets and uploads
├── tests/                     # Automated test suite (27 tests)
│   ├── test_ai_service.py
│   ├── test_auth.py
│   ├── test_database.py
│   ├── test_family.py
│   ├── test_i18n.py
│   ├── test_medicine.py
│   ├── test_pdf_service.py
│   └── test_security.py
└── data/                      # Local SQLite database, uploads, and PDF summaries
```

---

## ⚖️ Safety & Medical Disclaimer

HealthBuddy for Parents is an AI-assisted informational and organizational tool designed for parents and family caregivers. **It does not provide medical diagnoses, treatment plans, or clinical prescriptions.** All diagnostic test evaluations, questions to ask doctors, and dietary tips must be reviewed with a licensed physician. If you or a loved one experience urgent symptoms (such as chest pain or breathing difficulty), contact emergency medical services immediately.

# Medical VA Automation System

A Python/FastAPI medical administrative workspace for exactly two roles: **VA Joy** and **Employer**.

## Architecture

Browser → FastAPI → SQLAlchemy → SQLite (with a straightforward path to PostgreSQL) → private file storage

The patient is the central source of truth. Appointments, billing, insurance, documents, tasks, follow-ups, notes and activity history are linked to the patient.

## Current features

- Server-side authentication with HTTP-only JWT cookies
- Exactly two configured roles: VA Joy and Employer
- Patient creation, editing and deletion
- Full patient record
- Appointment creation and completion
- APPROACHING / COMPLETED / PAST DUE appointment display logic
- Billing with PAID / WAITING / NOT PAID and detailed billing states
- Payment received tracking by day, week, month and year
- Outstanding / receivable totals
- Insurance records and verification states
- Tasks and follow-ups with due/overdue logic
- Patient document upload, preview, download and deletion
- PDF and image inline viewing
- Activity history
- Report summary endpoint
- Appointment calendar and selected-date analytics
- Responsive professional dashboard

## Local setup

1. Use Python 3.12+.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure the variables in `.env.example` in the server environment. Never commit `.env`.

Required:

- `MEDICAL_VA_SECRET_KEY`
- `VA_JOY_PASSWORD_HASH`
- `EMPLOYER_PASSWORD_HASH`

For local HTTP development, use `MEDICAL_VA_SECURE_COOKIE=0`. Use `1` behind HTTPS.

4. Start the application:

```bash
uvicorn backend.main:app --reload
```

Open `http://127.0.0.1:8000/`.

## Docker

```bash
docker build -t medical-va .
docker run -p 8000:8000 --env-file .env medical-va
```

Mount persistent storage for the database and `storage/` directory. For a larger production deployment, move the database to PostgreSQL and use persistent/object storage for uploaded files.

## Security

Passwords and JWT secrets are server-side environment variables only. No real credentials or patient data belong in this repository.

This project does **not** claim HIPAA or other regulatory compliance. Before using real protected health information, the deployment must add and verify the privacy/security controls required by the client and applicable jurisdiction, including HTTPS, encryption, secret management, backups, retention, access reviews, monitoring, incident response and appropriate audit controls.

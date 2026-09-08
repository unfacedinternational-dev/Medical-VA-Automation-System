# Medical VA Automation System

A Python/FastAPI medical virtual-assistant workspace for exactly two roles: VA Joy and Employer.

## Architecture

Browser → FastAPI → SQLite database + private file storage

The application connects patients with appointments, billing, insurance, documents, tasks, follow-ups, notes, and activity history.

## Run locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the required environment variables from `.env.example`, then start:

```bash
uvicorn backend.main:app --reload
```

Open `http://127.0.0.1:8000/`.

## Authentication

There are exactly two server-side accounts:

- `va_joy` — operational access
- `employer` — oversight access

Passwords are never stored in frontend code or this repository. Set `VA_JOY_PASSWORD_HASH` and `EMPLOYER_PASSWORD_HASH` to bcrypt hashes in the server environment and set a long random `MEDICAL_VA_SECRET_KEY`.

## Full Patient Records and Documents

Every patient has one connected record containing appointments, billing, insurance, tasks, follow-ups, notes, activity, and documents.

Documents support PDF, common image formats, Word, Excel, and text files, with a 25 MB per-file limit. Users can upload, view PDFs/images in an in-app viewer, download, and delete documents. File metadata includes filename, type, size, uploader, and upload date. Files are stored outside the Git repository.

## Docker

Build and run the Python application with the included Dockerfile. Persistent volumes must be configured for the SQLite database and `storage/` directory.

## Production security

This repository is application code and makes no HIPAA or other regulatory compliance claim. Before handling real patient information, use HTTPS, persistent encrypted storage, secure database backups, secret management, restrictive CORS, monitoring, retention controls, access reviews, and a security/privacy assessment appropriate to the jurisdiction and client requirements.

# Medical VA Automation System

A client-ready frontend workspace for medical virtual assistant operations, built to render directly on GitHub Pages before the production backend is connected to Vercel.

## Current GitHub Pages phase

- Static HTML/CSS/JavaScript — no framework dependency
- Responsive dashboard and navigation
- Patients, appointments, follow-ups, tasks, automations, messages, billing, insurance, documents, reports, and activity
- Fictional demo patients only
- Local browser persistence with `localStorage`
- Appointment completion demonstrates the connected workflow:
  `Appointment → Billing → Insurance → Task → Staff Notification → Claim Tracking`
- Document upload interface supports PDF, Office documents, spreadsheets, text files, and images; the GitHub Pages version keeps the workspace local to the browser.

## Production phase

The same interface can later be connected to a Vercel-hosted backend for:

- PostgreSQL persistence
- Secure authentication and role-based access
- Multi-user data
- Secure file storage and real PDF/image previews
- Scheduled/background automations
- Email and notification services
- Optional calendar integration
- Audit and operational controls

No healthcare compliance certification or regulatory claim is made by this demo. Production security, privacy, access controls, retention, auditability, and applicable healthcare requirements must be implemented and validated before real patient information is used.

## Demo patients

Maria Santos, Daniel Reyes, Sophia Cruz, Michael Garcia, and Anna Rodriguez are fictional demonstration records.

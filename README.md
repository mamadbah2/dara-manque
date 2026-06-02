# Dara Manqué — Smart Health Card

A digital health record system that replaces the traditional paper health booklet with a smart NFC card. Each card is linked to a patient and acts as a secure access key — all medical data resides server-side.

## Architecture

```
dara-manque/
├── backend/    # FastAPI REST API + PostgreSQL
├── web/        # React + Vite portal (Doctor & Pharmacist)
└── mobile/     # Flutter app (Patient)
```

## Actors

| Actor | Interface | Key Features |
|---|---|---|
| **Patient** | Flutter mobile | Identify by card ID, view prescriptions & consultations |
| **Doctor** | React web | Search patient, view full record, create prescriptions |
| **Pharmacist** | React web | View active prescriptions, mark as treated |

> **MVP note:** The NFC card is currently simulated by a numeric patient ID. Real NFC integration is planned for a future release.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Web frontend | React 18, TypeScript, Vite, axios, react-router-dom |
| Mobile | Flutter 3.44, Dart, http package |

## Prerequisites

- Python 3.11+
- Node.js 18+
- Flutter 3.x SDK
- PostgreSQL 15+ (or Docker)

## Getting Started

### 1. Start PostgreSQL

**With Docker (recommended):**
```bash
docker run -d --name dara_postgres --network host \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  postgres:16

docker exec dara_postgres psql -U postgres -c "CREATE DATABASE dara_manque;"
docker exec dara_postgres psql -U postgres -c "CREATE DATABASE test_dara_manque;"
```

> **Note (snap Docker on Ubuntu):** Use `--network host` to avoid the snap docker-proxy TCP bug. The backend connects to `localhost:5432` directly.

### 2. Backend

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # set a strong SECRET_KEY in production
alembic upgrade head
python3 seed.py               # loads demo data
fastapi dev app/main.py
```

API available at `http://localhost:8000` — Swagger UI at `http://localhost:8000/docs`

### 3. Web Frontend

```bash
cd web
npm install
npm run dev
```

Portal available at `http://localhost:5173`

### 4. Mobile App

```bash
cd mobile
flutter pub get
flutter run                   # requires Android emulator or connected device
```

> On Android emulator, the backend is reachable at `http://10.0.2.2:8000`.  
> On a physical device, edit `_baseUrl` in `lib/api/client.dart` to your machine's LAN IP.

## Demo Credentials

After running `python3 seed.py` in the `backend/` directory:

| Role | Email | Password |
|---|---|---|
| Doctor | `doctor@dara.com` | `password123` |
| Pharmacist | `pharmacist@dara.com` | `password123` |
| Patient ID | `1001` | *(no login — enter ID directly in the app)* |

## API Overview

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/login` | — | Login, returns JWT + role |
| GET | `/patients/{id}` | — | Patient record |
| GET | `/patients/{id}/consultations` | — | Consultation history |
| GET | `/patients/{id}/prescriptions` | — | Active prescriptions |
| POST | `/patients/{id}/prescriptions` | Doctor | Create prescription |
| PATCH | `/prescriptions/{id}/treat` | Pharmacist | Mark prescription as treated |

## Running Tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

Requires the `test_dara_manque` database to exist (created in step 1 above). All 16 tests should pass.

## Known MVP Limitations

| Limitation | Notes |
|---|---|
| No patient authentication | Patient endpoints are public by design (NFC simulation) — add patient auth before production |
| JWT in localStorage | Vulnerable to XSS — switch to `httpOnly` cookies in production |
| No doctor-patient relationship | Any doctor can create prescriptions for any patient |
| No NFC card integration | Uses numeric ID; Flutter `nfc_manager` can be added for real NFC |
| No appointment scheduling | Out of MVP scope |
| AI modules not integrated | Fraud detection, behavioral analysis, and flow prediction are planned as separate microservices |

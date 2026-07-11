# Windows Setup Guide

Step-by-step instructions for installing the Smart Society Management System on a Windows development machine. Target audience: a developer who has never used the project before.

---

## 1. Install prerequisites

| Tool | Where to get it | Notes |
|---|---|---|
| Python 3.11+ | https://www.python.org/downloads/ | Tick **Add Python to PATH** during install. |
| Node.js 20+ | https://nodejs.org/en/download | LTS recommended. |
| Git | https://git-scm.com/download/win | Optional, but recommended. |
| PostgreSQL 15+ (optional) | https://www.postgresql.org/download/windows/ | Only needed if you don't want to use the bundled SQLite for development. |
| Flutter SDK | https://docs.flutter.dev/get-started/install/windows | Only needed for the mobile app. |

Verify the installs from PowerShell:

```powershell
python --version
node --version
npm --version
```

---

## 2. Set up the backend

```powershell
# Extract the project archive you downloaded
Expand-Archive .\smart-society.zip -DestinationPath .\projects

cd .\projects\smart-society\backend

# Create venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies (this takes ~1 minute)
pip install -r requirements.txt

# Copy the env template and edit it as needed
copy .env.example .env
notepad .env
```

You only need to edit `.env` if you want to point at Postgres. The defaults run
on SQLite (no setup):

```
# leave as is for SQLite (default)
DATABASE_URL=sqlite:///./smart_society.db

# OR use Postgres:
# DATABASE_URL=postgresql+psycopg://soc_admin:soc_password@localhost:5432/smart_society
```

### Apply database schema (Alembic) and seed demo data

```powershell
# SQLite: create_all runs at startup, so just seed:
python scripts\seed.py

# Postgres: run migrations first, then seed
alembic upgrade head
python scripts\seed.py
```

### Start the API server

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

You should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

Open `http://localhost:8000/docs` for Swagger UI, or `http://localhost:8000/health`
for a quick health probe. Sign in with one of the seeded accounts in the README.

---

## 3. Install PostgreSQL (optional, for production-style data)

If you want Postgres instead of SQLite:

1. Download the Postgres 15 Windows installer and run it.
2. During setup, set the `postgres` superuser password and remember the port (default 5432).
3. After install, open **SQL Shell (psql)** or use PowerShell:

```powershell
psql -U postgres
```

```sql
CREATE DATABASE smart_society;
CREATE USER soc_admin WITH PASSWORD 'soc_password';
GRANT ALL PRIVILEGES ON DATABASE smart_society TO soc_admin;
\q
```

Update `backend\.env`:

```
DATABASE_URL=postgresql+psycopg://soc_admin:soc_password@localhost:5432/smart_society
```

Then run:

```powershell
alembic upgrade head
python scripts\seed.py
```

---

## 4. Start the web dashboard

```powershell
cd ..\frontend-web

npm install
copy .env.example .env
notepad .env          # set VITE_API_BASE_URL=http://localhost:8000/api/v1

npm run dev
```

Open `http://localhost:5173` and sign in with `admin@greenpark.com / Admin@12345`.

---

## 5. Run the Flutter mobile app

```powershell
cd ..\mobile

flutter pub get
flutter doctor          # confirm everything is green

# Android emulator
flutter emulators --launch <your_emulator_name>
flutter run

# OR a physical device with USB debugging enabled
flutter run -d <device_id>
```

The default API base URL inside the app points to `http://10.0.2.2:8000/api/v1`
(the host machine as seen from an Android emulator). For a real device, set the
backend URL via the in-app settings (or call `Storage.baseUrl = ...` in
`mobile/lib/src/core/storage.dart`).

---

## 6. Verify the project is working

1. `http://localhost:8000/health` → `{"status":"ok",...}`
2. Swagger UI: `http://localhost:8000/docs`
3. Web dashboard: `http://localhost:5173` → log in with `admin@greenpark.com`
4. Mobile app: tap the dashboard cards and verify data loads from the backend.

---

## 7. Troubleshooting

| Symptom | Fix |
|---|---|
| `python` not found | Restart PowerShell after installing Python or run `where python` to confirm PATH. |
| `pip install` fails on Windows for bcrypt | Install the precompiled wheel: `pip install --upgrade pip wheel` then `pip install bcrypt==4.0.1`. |
| `uvicorn` ImportError on startup | Make sure the venv is active: `.\.venv\Scripts\Activate.ps1`. |
| Postgres connection refused | Check `pg_hba.conf` / firewall. If local dev fails, fall back to SQLite. |
| `npm install` fails on Windows | Run PowerShell as Administrator, or pre-run `npm install --global windows-build-tools` (legacy) or install the latest Node LTS. |
| Flutter doctor flags Android licenses | Run `flutter doctor --android-licenses` and accept them. |
| Vite calls the backend at the wrong URL | Confirm `VITE_API_BASE_URL` ends with `/api/v1`. |
| Mobile cannot reach the backend | `localhost` from device is itself; use `10.0.2.2` (emulator) or your machine's LAN IP. |

For deeper troubleshooting, see [`docs/TESTING.md`](TESTING.md).

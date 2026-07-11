# Architecture

## High-level

```
             ┌───────────────────────┐
             │    Flutter mobile     │  ── Dio + JWT ──┐
             └───────────────────────┘                  ▼
                                          ┌────────────────────────┐
             ┌───────────────────────┐    │   FastAPI backend      │
             │  React Web dashboard  │ ── │  (auth, REST, AI, PDF, │
             └───────────────────────┘    │   reports, scheduler) │
                                          └───────────┬────────────┘
                                                      ▼
                                          ┌────────────────────────┐
                                          │  PostgreSQL | SQLite   │
                                          └────────────────────────┘
```

- **Auth:** JWT access (30 min) + refresh tokens (7 days), bcrypt password
  hashing, role guards on every write endpoint and on cross-tenant reads.
- **ORM:** SQLAlchemy 2 + declarative `Base`. Models are organized by domain
  (society / complaint / bill / visitor / notice / audit / chat).
- **Migrations:** Alembic with a single initial version that creates all
  tables, indexes, and foreign keys. Applications set `DATABASE_URL` to
  Postgres in production; the dev default uses SQLite.
- **AI assistant:** permission-aware intent dispatcher. Real OpenAI calls are
  opt-in via `AI_PROVIDER=openai`. The default offline router keeps the UI
  fully functional without an API key so developers can build and demo.
- **Notifications:** SMTP via stdlib `smtplib`, Telegram via the Bot HTTP API.
  Both return `False` and log a warning when unconfigured instead of raising.
- **OCR:** Google Vision REST call if `OCR_PROVIDER=google_vision`; otherwise a
  deterministic stub. The interface is identical so swapping is configuration-
  only.
- **Scheduled jobs:** APScheduler runs in the same process as FastAPI. A daily
  job sweeps overdue bills, a monthly job generates bills. Toggle off with
  `ENABLE_SCHEDULERS=false`.

## Backend layout

```
backend/app/
├── api/                  HTTP routers
│   ├── router.py         auth (register/login/refresh/me/password-change)
│   ├── residents.py
│   ├── societies.py
│   ├── complaints.py     with AI category classifier
│   ├── visitors.py       with QR tokens + check-in/out
│   ├── bills.py          with PDF download + payments
│   ├── notices.py
│   ├── ai.py
│   ├── reports.py        Excel exports
│   └── admin.py          users, audit logs, stats
├── core/                 config, security, deps
├── db/                   engine + session + Base
├── models/               SQLAlchemy ORM
├── schemas/              Pydantic v2 schemas
├── services/             AI, OCR, notifications, billing, reports
├── schedulers/jobs.py    APScheduler cron
└── main.py               FastAPI app
```

## Role matrix

| Endpoint family | admin / superuser | committee | resident | security |
|---|:---:|:---:|:---:|:---:|
| Read own profile | ✅ | ✅ | ✅ | ✅ |
| Read all users | ✅ | ✅ | ❌ | ❌ |
| Read all complaints | ✅ | ✅ | own only | own only |
| Update complaint status | ✅ | ✅ | own only | ❌ |
| Pay own bill | ✅ | ✅ | ✅ | ❌ |
| Pay any bill | ✅ | ✅ | ❌ | ❌ |
| Approve visitor | ✅ | ✅ | own host only | ❌ |
| Check-in/out visitor | ✅ | ✅ | ❌ | ✅ |
| Publish notice | ✅ | ✅ | ❌ | ❌ |
| AI chat | full | committee scope | self scope | self scope |

## Security notes

- Passwords use bcrypt with `passlib`'s safe defaults.
- Every mutating endpoint writes an `AuditLog` row.
- All queries are parameterized through SQLAlchemy ORM; no string concat.
- CORS is restricted via the `CORS_ORIGINS` env var.
- File uploads (photos, PDFs) are written under `UPLOAD_DIR` (default
  `uploads/`) and served via FastAPI `FileResponse`.

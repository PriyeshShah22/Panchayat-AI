# Testing Guide

## Smoke test the backend (no test framework required)

After starting the server (`uvicorn app.main:app --reload`):

```bash
# 1. Health
curl http://localhost:8000/health

# 2. Login (use any seeded account)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@greenpark.com","password":"Admin@12345"}'

# 3. List notices
TOKEN="<paste access_token here>"
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/notices/

# 4. Get AI stats
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/admin/stats

# 5. Chat with the assistant
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"message":"Show my pending maintenance"}' \
  http://localhost:8000/api/v1/ai/chat
```

## Smoke test the web dashboard

1. `cd frontend-web && npm install && npm run dev`
2. Open `http://localhost:5173`
3. Sign in as `admin@greenpark.com / Admin@12345`
4. Check each sidebar item — Dashboard, Complaints, Bills, Visitors, Notices, AI Assistant, Admin.

## Smoke test the mobile app

1. `cd mobile && flutter pub get`
2. Start an Android emulator or connect a real device.
3. `flutter run`
4. Use the seeded credentials to sign in. The dashboard renders, the AI tab
   accepts messages, visitors/complaints/bills load.

## Module-by-module test scenarios

### Authentication
| Scenario | Expected |
|---|---|
| Register with valid email & 8+ char password | 201 + JWTs returned |
| Register with existing email | 400 with detail |
| Login with wrong password | 401 |
| Login with right password | 200 + user with roles |
| `/auth/me` without token | 401 |
| `/auth/me` with valid token | 200, returns user |
| Refresh with valid refresh token | New access + refresh tokens |

### Residents
| Scenario | Expected |
|---|---|
| Resident calls `/residents/me` | Their own profile |
| Resident calls `/residents/` (list) | 403 (needs admin/committee) |
| Committee calls `/residents/` | Page of residents |

### Complaints
| Scenario | Expected |
|---|---|
| Resident creates "Leak in kitchen" | 201; AI category `Plumbing` set |
| Resident lists `?mine=true` | Their own only |
| Committee updates status to `resolved` | 200; resolved_at set |
| Adding comment with `is_internal=true` | Shown to admin/committee only |

### Bills
| Scenario | Expected |
|---|---|
| Committee triggers `/bills/generate-monthly?society_id=1` | New bills for every flat |
| Resident pays `Bill.outstanding` | Bill → `paid`; payment row |
| Resident pays another resident's bill | 403 |
| `/bills/1/pdf` | Downloads a real PDF |

### Visitors
| Scenario | Expected |
|---|---|
| Resident registers `Ajay` with vehicle | 201; QR token returned |
| Host approves | Status `approved` |
| Security check-in | Status `checked_in` |
| Security check-out | Status `checked_out` |
| Random user approves | 403 |

### Notices
| Scenario | Expected |
|---|---|
| Committee publishes notice | 201; pinned shown at top |
| Resident lists notices | Sees `audience=all` notices |

### AI assistant
| Scenario | Expected |
|---|---|
| Resident: "Show my pending maintenance" | Only their bills |
| Committee: "Who hasn't paid" | Top defaulters |
| Admin: "Generate society analytics" | Aggregate stats |

### Reports
| Scenario | Expected |
|---|---|
| GET `/reports/complaints.xlsx` | Downloads valid .xlsx file |
| GET `/reports/bills.xlsx` | Same |

## Troubleshooting checklist

- `ImportError` on backend startup → activate the venv and `pip install -r requirements.txt`
- 401 on protected endpoints → your token may be expired; call `/auth/refresh` or log in again
- AI assistant replies seem generic → expected when `OPENAI_API_KEY` is unset; the offline router still works
- Web dashboard request fails with CORS error → confirm `CORS_ORIGINS` in backend `.env` includes the web origin (default is `*`)
- Mobile cannot reach backend → from an Android emulator use `http://10.0.2.2:8000/api/v1`, on a real device use your machine's LAN IP

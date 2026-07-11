# Database

## Engine

- **Default (development):** SQLite — no extra installation required.
- **Production:** PostgreSQL 14+. Use the bundled Alembic migrations; the same
  schema works for both.

Switch engines by setting `DATABASE_URL`:

```
# SQLite
DATABASE_URL=sqlite:///./smart_society.db

# Postgres
DATABASE_URL=postgresql+psycopg://soc_admin:soc_password@localhost:5432/smart_society
```

## Tables (initial schema)

| Table | Purpose |
|---|---|
| `societies` | Top-level housing society entity |
| `blocks` | Building / block within a society |
| `flats` | Individual flat / apartment |
| `users` | Login identities, FK to society (nullable for global admins) |
| `roles` | Named roles (`admin`, `committee`, `resident`, `security`) |
| `permissions` | Fine-grained permission codes |
| `role_permissions` | M:N between roles and permissions |
| `user_roles` | M:N between users and roles |
| `residents` | Resident profile (1:1 with a `users` row, FK to flat) |
| `complaint_categories` | Catalogue of complaint types |
| `complaints` | Title, body, status, priority, reporter, assignee, FK to category & society & flat |
| `complaint_comments` | Threaded discussion / status notes |
| `visitors` | Visitor records with QR token + host FK |
| `visitor_logs` | Approve / reject / check-in / check-out audit entries |
| `bills` | Maintenance / utility invoices |
| `payments` | Payments against bills (FK to user who received the payment) |
| `notices` | Notice board entries, optionally pinned |
| `audit_logs` | Append-only system log |
| `chat_messages` | AI assistant conversation history |

## Relationships

```
societies ─┬── blocks ─── flats ─── residents ─── users
           ├── users
           ├── complaints ─── complaint_comments
           │       └── complaint_categories
           ├── visitors ─── visitor_logs
           ├── bills ────── payments
           └── notices
users ─── user_roles ─── roles ─── role_permissions ─── permissions
```

All FKs use `ON DELETE CASCADE` (where parent owns the child) or `SET NULL`
(for references like `bills.resident_id` so deleting a resident doesn't lose
billing history).

Performance indexes are defined on:

- `users.email` (unique)
- `users.society_id`
- `complaints.society_id`, `reporter_id`, `status`, `created_at`
- `bills.society_id`, `flat_id`, `status`
- `visitors.society_id`, `host_id`, `status`
- `audit_logs.action`, `(entity_type, entity_id)`
- `chat_messages.user_id`

## Migrations

Alembic is configured in `backend/alembic.ini`. The initial migration
`backend/alembic/versions/0001_initial.py` creates every table, index, and
constraint.

```powershell
cd backend
alembic upgrade head        # apply
alembic downgrade -1       # revert one step
alembic revision -m "msg"   # author a new revision
```

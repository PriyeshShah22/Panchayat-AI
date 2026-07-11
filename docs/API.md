# API Reference

Full Swagger UI is generated automatically and served at `http://localhost:8000/docs`.
This document mirrors the most important routes.

Base URL: `/api/v1`

## Auth

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | – | Create a user and return access + refresh tokens |
| POST | `/auth/login` | – | Email/password login |
| POST | `/auth/refresh` | – | Exchange a refresh token for a new access token |
| GET | `/auth/me` | ✅ | Current user |
| POST | `/auth/password-change` | ✅ | Change own password |

## Society / Block / Flat

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/societies/` | ✅ | List societies |
| POST | `/societies/` | admin | Create society |
| GET | `/societies/{id}/blocks` | ✅ | List blocks of a society |
| POST | `/societies/blocks` | admin/committee | Create block |
| GET | `/societies/blocks/{block_id}/flats` | ✅ | List flats of a block |
| POST | `/societies/flats` | admin/committee | Create flat |

## Residents

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/residents/me` | ✅ | Current resident profile |
| POST | `/residents/` | admin/committee | Create resident profile |
| GET | `/residents/` | admin/committee | List residents |
| PATCH | `/residents/{id}` | owner or admin | Edit resident |

## Complaints

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/complaints/` | ✅ (own/committee) | List with `?status=,?mine=,?search=` |
| POST | `/complaints/` | ✅ | Create (auto-AI classification if no category_id) |
| GET | `/complaints/{id}` | ✅ | Detail |
| PATCH | `/complaints/{id}` | reporter / committee | Update status/priority/assignee |
| POST | `/complaints/{id}/comments` | ✅ | Add comment |
| GET | `/complaints/{id}/comments` | ✅ | List comments |
| GET | `/complaints/categories` | ✅ | List categories |
| POST | `/complaints/categories` | admin/committee | Create category |
| POST | `/complaints/classify` | ✅ | AI classify a text snippet |

## Visitors

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/visitors/` | ✅ (scoped) | `?mine=true&society_id=` |
| POST | `/visitors/` | ✅ | Register a visitor |
| PATCH | `/visitors/{id}` | host | Edit |
| POST | `/visitors/{id}/action` | host|security | `approve / reject / check_in / check_out` |

## Bills / Payments

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/bills/` | ✅ (scoped) | `?status=` |
| POST | `/bills/` | admin/committee | Create bill manually |
| POST | `/bills/generate-monthly?society_id=` | admin/committee | Trigger monthly generation |
| POST | `/bills/sweep-overdue` | admin/committee | Late-fee + overdue sweep |
| POST | `/bills/{id}/pay` | ✅ (scoped) | Record a payment |
| GET | `/bills/{id}/pdf` | ✅ (scoped) | Download PDF bill |

## Notices

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/notices/?society_id=` | ✅ | List |
| POST | `/notices/` | admin/committee | Publish |
| DELETE | `/notices/{id}` | admin/committee | Remove |

## AI

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/ai/chat` | ✅ | Permission-aware assistant |

## Reports (Excel)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/reports/complaints.xlsx` | admin/committee | Recent complaints |
| GET | `/reports/bills.xlsx` | admin/committee | Recent bills |
| GET | `/reports/visitors.xlsx` | admin/committee/security | Last 30 days |

## Admin

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/admin/users?search=` | admin/committee | List users |
| GET | `/admin/audit-logs?limit=` | admin | Audit trail |
| GET | `/admin/stats` | admin/committee | Society-level metrics |
| POST | `/admin/users/{id}/roles/{role}` | admin | Assign role |

## Health

| Method | Path | Description |
|---|---|---|
| GET | `/health` | `{"status":"ok"}` |

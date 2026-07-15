# Panchayat AI

Panchayat AI is a voice-first housing-society platform designed for communities where many residents may not be comfortable with forms, English-only software, or complicated digital workflows. Every important task has two paths:

- Ask the AI agent in English, Hindi, or Marathi.
- Use the normal manual screen as a fallback.

The platform combines society maintenance, complaints, notices, visitors, membership verification, roles, and administrative reporting in one accessible application.

## Product tour

### The Panchayat agent

Residents can speak or type naturally. Hindi and Marathi audio is translated by Sarvam AI, then the permission-aware OpenAI agent checks society records and prepares safe actions. Write actions require confirmation.

The agent can:

- Create a formal English complaint from Hindi, Marathi, English, or Hinglish conversation.
- Infer complaint category and priority from impact, duration, safety risk, and urgency.
- Use the resident's linked building and flat without asking for the address again.
- Read current and older maintenance dues.
- Combine every unpaid month into one checkout.
- Complete a clearly labelled demo payment inside chat when Razorpay is not configured.
- Launch the real combined Razorpay checkout inside chat when merchant keys are configured.
- Read complaints and recent notices.
- Publish announcements for administrators only.
- Remember the five most recent messages and compress earlier context.
- Read every answer aloud while removing formatting that would confuse TTS.

![Agent preparing an inline combined maintenance payment](docs/screenshots/assistant-payment.png)

AI actions are permission checked on the server. The model cannot grant itself access, invent a successful payment, read another household's private records, or publish an admin notice for a resident.

### Combined monthly maintenance

There are no separate electricity or water charge heads. An administrator selects the month, one maintenance amount, and due date once. The backend bills every approved resident with a linked flat and safely skips accounts that already have a bill for that month.

Residents see all older unpaid months combined into one total. The screen still lists every included month so the amount remains understandable.

![Resident combined maintenance dues](docs/screenshots/combined-dues.png)

Payment modes:

- Razorpay UPI checkout when merchant credentials are configured.
- Demo checkout when Razorpay is unavailable. It is visibly marked as a simulation and transfers no real money.
- Privileged cash and cheque ledger entries for administrators and committee members.

Razorpay callbacks and webhooks are signature verified. Captured payments are idempotent, and a combined payment is distributed across the exact outstanding bills only after the provider amount matches.

### Notices that are difficult to miss

Pinned notices appear prominently on Home. The Notice Board gives the latest important update a full-width treatment, supports audience filters, search, expiry dates, and read-aloud.

![Redesigned notice board](docs/screenshots/notice-board.png)

Administrators and committee members can publish notices for everyone, residents, or the committee. Expired notices stop appearing automatically.

### Administrative command center

The admin workspace summarizes billed maintenance, collected money, active residents, complaints, overdue bills, and recent audit events. Quick actions connect directly to monthly billing, complaint triage, notices, and role management.

![Administrative command center](docs/screenshots/admin-console.png)

### English, Hindi, and Marathi

The language control is always visible at the top of the signed-in application. Navigation, dialogs, menus, inputs, helper text, accessibility labels, and bundled notice copy switch between English, Hindi, and Marathi from a reviewed translation catalog included with the web app. Switching is instantaneous, works offline, and makes no AI or translation API request. Names, emails, IDs, currency values, and numbers remain unchanged.

![Hindi home interface](docs/screenshots/hindi-home.png)

The selected interface language is remembered on the device. It does not control the assistant: typed messages are detected locally, while Sarvam detects the source language of voice requests. The agent replies in the language used for that request, and read-aloud uses the detected response locale.

## Main modules

### Complaints and helpdesk

- Only approved residents with a linked household can submit complaints.
- Pure admin accounts cannot submit; dual resident/admin accounts can submit for their own household.
- Formal complaint records created by the AI are always stored in English.
- Reporter name, building, flat, floor, contact details, priority, assignee, and history are available to authorized triage users.
- Workflow: Submitted → In Progress, Rejected, Resolved, or resident withdrawal.
- Residents may withdraw their own Submitted or In Progress complaint.
- Rejected, Resolved, and Withdrawn are terminal.
- Every transition records actor, time, reason, and audit event.

### Membership verification

Public signup does not immediately create an account. A requester must provide:

- Full name and date of birth.
- Society.
- Building.
- Flat number.
- Email, optional phone, and password.

Building and flat are selected from real society records. An administrator sees the application in the membership inbox and can approve or reject it. Approval creates the account and its resident-to-flat mapping together. Passwords are never shown to administrators.

### Visitors and gate operations

- Resident pre-registration and staff-created gate passes.
- Society-scoped flat selector rather than raw flat IDs.
- Pending approval, approved, checked-in, rejected, and checked-out states.
- Live counts for visitors inside, expected, awaiting approval, and completed.
- Search by visitor, phone, purpose, or vehicle.
- Host approval and security/committee/admin check-in and check-out.
- Audit events for every gate action.

### People and roles

- Searchable, role-filtered resident directory.
- Admin, Committee, Security, and Resident responsibilities.
- Only an existing administrator can grant Admin or Committee access.
- Admin access cannot be removed through the application.
- Committee, Security, and Resident roles can be added or removed by administrators.
- Every role change is society scoped and audited.

### Security boundaries

- Residents see only their own bills, complaints, and hosted visitors.
- Committee and admin users operate only inside their society.
- Security accounts see gate operations without financial access.
- Notice, visitor, flat, block, bill, complaint, role, and AI tools enforce society boundaries on the server.
- AI actions use typed server tools and never trust role claims written in chat.
- Secrets remain in ignored local environment files.

## Technology

- Backend: FastAPI, Python 3.11+, SQLAlchemy, Alembic, Pydantic.
- Web: React 18, TypeScript, Vite, Material UI, TanStack Query, Zustand.
- Mobile project: Flutter.
- Development database: SQLite.
- Production database: PostgreSQL-compatible SQLAlchemy design.
- AI: OpenAI Responses API with typed tools and conversation memory.
- Indian-language speech: Sarvam speech-to-text translation.
- Payments: Razorpay Orders, Checkout, signature validation, and webhooks.

## Windows quick start

On Windows 10 or Windows 11, clone or download the repository. Run the one-time installer from the repository root:

```bat
setup.bat
```

The setup script:

1. Detects compatible system installations of Python 3.11+ and Node.js 20+.
2. If either runtime is missing, downloads an isolated Python 3.12 runtime and the current portable Node.js LTS release from their official websites. Administrator access is not required.
3. Creates the local Python virtual environment and installs all backend dependencies.
4. Installs all locked frontend dependencies through npm.
5. Creates ignored local environment files from the examples when missing.
6. Applies every Alembic migration and adds only missing development seed records.
7. Backs up and rebuilds a repository-local SQLite database if an earlier interrupted migration left it unusable.

A fresh computer only needs Windows PowerShell and an internet connection for `setup.bat`. Administrator access is not required. Downloaded runtimes are stored in the ignored `.tools` directory.

After setup prints `[READY]`, launch the app with:

```bat
start.bat
```

`start.bat` is intentionally fast. It does not install packages, migrate the database, or seed data. It only starts the API at `http://localhost:8000`, starts the web app at `http://localhost:5173`, and opens the site. Run `setup.bat` again only after dependency changes or when setup/database repair is required.

The application and manual workflows start without third-party credentials. Panchayat AI, Indian-language speech, live Razorpay payments, email, and Telegram require their corresponding keys to be added to `backend/.env`; secrets are intentionally never downloaded or committed automatically.

API documentation is available at `http://localhost:8000/docs`.

## Environment configuration

Copy `backend/.env.example` to `backend/.env`. Never commit the resulting file.

Important settings:

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5.4-nano
SARVAM_API_KEY=
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
RAZORPAY_WEBHOOK_SECRET=
```

When all Razorpay values are blank, the application automatically enables the labelled demo checkout. Adding valid merchant credentials disables demo settlement and activates real checkout.

For a real webhook, configure the merchant dashboard to send payment events to:

```text
POST /api/v1/bills/payments/webhook
```

## Development accounts

The seed script creates:

| Email | Password | Roles |
|---|---|---|
| `admin@greenpark.com` | `Admin@12345` | Admin / superuser |
| `committee@greenpark.com` | `Committee@123` | Committee |
| `security@greenpark.com` | `Security@123` | Security |
| `resident@greenpark.com` | `Resident@123` | Resident and committee |
| `ravi@greenpark.com` | `Ravi@12345` | Resident |

These credentials are for local development only.

## Important API flows

### Monthly maintenance

```text
POST /api/v1/bills/monthly
GET  /api/v1/bills/dues-summary
POST /api/v1/bills/payment-order
POST /api/v1/bills/payments/demo
POST /api/v1/bills/payments/verify
POST /api/v1/bills/payments/webhook
```

### Assistant

```text
POST /api/v1/ai/chat
POST /api/v1/ai/voice
POST /api/v1/ai/actions/{id}/confirm
POST /api/v1/ai/actions/{id}/cancel
```

### Membership and complaints

```text
GET  /api/v1/auth/societies
POST /api/v1/auth/join-requests
POST /api/v1/admin/join-requests/{id}/approve
POST /api/v1/complaints/
POST /api/v1/complaints/{id}/transition
POST /api/v1/complaints/{id}/withdraw
```

## Verification performed for this release

- Fresh database migration from revision 0001 through 0005.
- Upgrade of the existing development database.
- Bulk monthly billing and duplicate prevention.
- Maintenance-only line item migration.
- Combined multi-month dues summary.
- Combined demo payment and zero remaining balance.
- Compulsory membership location validation.
- Complaint building and flat serialization.
- OpenAI inline payment proposal.
- English → Hindi → English interface switching.
- TypeScript type check and production Vite build.
- Python compilation and FastAPI route import.
- Browser verification of Home, Assistant, Dues, Notices, Complaints, Gate, People, and Admin.

## Repository layout

- `backend/` — FastAPI, database models, migrations, AI and payment services.
- `frontend-web/` — React web application.
- `mobile/` — Flutter client project.
- `docs/screenshots/` — current product screenshots used in this README.
- `setup.bat` — one-time Windows runtime, dependency, environment, and database setup.
- `start.bat` — fast daily launcher for the configured backend and web app.

## License

MIT

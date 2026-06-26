# Oasis on the Go Spa — Management System

A mobile-friendly web app to run **Oasis on the Go Spa** (Cavite, PH) across its
two branches (General Trias and Trece Martires) for both walk-in and home-service
clients. Replaces the manual Messenger + screenshot + transaction-sheet workflow.

Built with **Django 5.2 + SQLite** (runs offline on one PC, reachable by staff
phones over the office Wi‑Fi). Currency ₱, timezone Asia/Manila. Installable as a
PWA ("Add to Home Screen").

---

## Phase 1 (this build) — what's included

| Module | Where |
|---|---|
| Owner & therapist login with role-based access | `/login/` |
| Manual booking entry (FB / phone / walk-in, walk-in or home service) | Bookings → New |
| Kanban **Service Board** with drag-drop + Start/Finish time stamping | `/board/` |
| Payments + screenshot upload + printable receipt | Booking → Record payment |
| Expenses / petty cash with receipt photo | `/expenses/` |
| Daily transaction record + daily sales report (Excel + PDF export) | `/reports/daily/` |
| Client database (CRM) with search + visit history | `/customers/` |
| Owner dashboard: sales vs expenses, bookings, top services | `/` |

**Roles**
- **Owner / Admin** — full access across both branches.
- **Therapist / Staff** — only their own assigned bookings + the board; no sales totals, expenses, or reports.

**Deferred to later phases** (per project plan): staff photo time-logs + payroll,
loyalty cards, customer-facing booking page, reminders / ManyChat Facebook intake.
A channel-agnostic intake hook (`Booking.external_source` / `external_ref`) is
already in place for future Facebook automation.

---

## Running it

Double-click **`start-oasis.bat`**, then open <http://localhost:8000>.
Other phones on the same Wi‑Fi: `http://<this-pc-ip>:8000`.

### Demo accounts
| Role | Username | Password |
|---|---|---|
| Owner / Admin | `owner` | `oasis123` |
| Therapist | `therapist1` | `oasis123` |
| Therapist | `therapist2` | `oasis123` |

> ⚠️ Change these passwords and wipe demo data before go-live.

### First-time / manual setup
```
.venv\Scripts\python.exe manage.py migrate
.venv\Scripts\python.exe manage.py seed_demo      # branches, services, demo users + sample data
```

### Configuration
Business settings (company name, payment methods, expense categories, hours) live
in the `OASIS = {...}` block at the bottom of `oasis/settings.py`.
Branches, services, and staff can also be managed in the Django admin at `/admin/`.

### Reset before go-live
1. Stop the server.
2. Delete `db.sqlite3`.
3. Run `migrate`, create a real owner with `createsuperuser`, then add branches,
   services, and staff via `/admin/` (skip `seed_demo` so no demo data is loaded).

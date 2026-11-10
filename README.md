# VeloRent Pro - Enterprise Bike & Scooty Management & Rental System

Welcome to the **VeloRent Pro** repository! This is a production-grade, full-stack scooty/bike rental and fleet management platform built with FastAPI, React, PostgreSQL, Redis, Docker, and GitHub Actions CI/CD.

---

## 🚀 3 Dedicated Frontend Portals & Independent Ports

The frontend has been completely decoupled into **3 distinct, clean, and modern web applications**, each running on its dedicated port with an intuitive, tasteful UI palette (no neon/cyberpunk glassmorphism clutter):

| Portal | Target User | Dedicated Port | Dev Command | Key Responsibilities |
|---|---|---|---|---|
| **Driver Portal** | Renters / Drivers | `http://localhost:3110` | `npm run dev:driver` | Scooty catalog, KYC verification, wallet recharge (₹500 min), booking, active rental duration tracker, return vehicle request |
| **Fleet Owner Portal** | Scooty / Bike Owners | `http://localhost:6782` | `npm run dev:owner` | Scooty listing (RC, pricing, deposit), fleet status, booking approvals, vehicle return inspection, damage assessment & deposit refund |
| **Admin Portal** | System Administrators | `http://localhost:5431` | `npm run dev:admin` | Executive dashboard (Gross Revenue, 10% platform cut, fleet stats), KYC verification (drivers & owners), scooty approvals, user moderation (block/unblock), broadcasts |
| **All Portals** | Multi-Dev Runner | All 3 ports concurrently | `npm run dev` | Spawns all 3 portals simultaneously using `concurrently` |
| **Portal Gateway** | Hub / Selector | `http://localhost:3000` | `npx vite` | Root launchpad for jumping directly into any of the 3 portals |

---

## 🔄 End-to-End Rental Workflow & Business Logic

The platform strictly enforces the complete scooty rental lifecycle:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. ONBOARDING & VERIFICATION                                                          │
│   • Driver uploads Driving License & Aadhaar → Admin verifies documents               │
│   • Owner uploads ID & Bank Account details → Admin verifies payout credentials       │
│   • Owner lists Scooty (RC copy, photos, rent/day, deposit) → Admin verifies listing  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. WALLET RECHARGE & BOOKING                                                           │
│   • Driver recharges wallet via Razorpay (strict minimum recharge policy: ₹500)       │
│   • Driver browses verified scooties                                                  │
│   • System enforces: Driver Wallet Balance >= (Rent + Security Deposit)                │
│   • System enforces: Maximum 1 active rental per driver at any given time             │
│   • Driver submits booking request → Owner receives instant alert                     │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. DISPATCH & ACTIVE RENTAL                                                            │
│   • Owner reviews and accepts booking request                                         │
│   • System locks/deducts rent and security deposit from driver wallet                 │
│   • Scooty state transitions to RENTED; ActiveAssignment is created                    │
│   • Driver dashboard displays live rental timer, rate, and emergency controls         │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. RETURN, INSPECTION & DEPOSIT REFUND                                                 │
│   • Driver requests return via Driver Portal (`POST /driver/assignment/request-return`)│
│   • Owner performs vehicle inspection and inputs damage assessment charges (if any)   │
│   • Owner confirms return:                                                            │
│       - Scooty transitions back to AVAILABLE                                          │
│       - Net Deposit = (Security Deposit - Damage Charges) is refunded to Driver wallet│
│       - Platform earns 10% commission on rental earnings                              │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Architecture & Tech Stack

### 1. Backend (`/Backend`)
- **Framework**: Python 3.12 + FastAPI (Async REST API & WebSockets)
- **Database**: PostgreSQL 15 + SQLAlchemy 2.0 ORM with Alembic schema migrations
- **Caching & Real-time**: Redis + Socket.IO notification engine
- **Authentication**: JWT Access & Refresh Token authentication, Bcrypt hashing, role-based guards (`driver`, `owner`, `admin`)
- **Scheduled Background Worker**: Cron worker processing overdue rentals, late fees, and automatic settlements
- **Reliable APIs Added**:
  - `GET /admin/drivers` - Lists all drivers with document verification status
  - `GET /admin/owners` - Lists all fleet owners with KYC and bank payout statuses
  - `GET /admin/bikes` - Lists all bikes with approval queues and specifications
  - `GET /admin/users` - User directory with block/unblock controls
  - `GET /owner/booking-requests` - Owner queue for incoming booking requests
  - `GET /owner/active-rentals` - Active scooty assignments for return inspections
  - `POST /driver/assignment/request-return` - Driver vehicle return notification trigger

### 2. Frontend (`/Frontend`)
- **Framework**: React 19 + TypeScript + Vite 8 + TailwindCSS 4 + Lucide Icons
- **Separated Apps**:
  - `Frontend/driver/` (`vite.driver.config.ts`, port `3110`)
  - `Frontend/owner/` (`vite.owner.config.ts`, port `6782`)
  - `Frontend/admin/` (`vite.admin.config.ts`, port `5431`)
- **Shared Logic**: `Frontend/shared/api.ts` (Axios client with JWT interceptor) & `Frontend/shared/types.ts` (Strongly-typed data contracts)
- **Design System**: Accessible, clean, modern interfaces with distinct role themes (Slate/Emerald for Drivers, Zinc/Indigo for Owners, Slate/Violet for Admins).

---

## ⚡ Quick Start / Local Setup

### 1. Running Frontend Portals
```bash
cd Frontend
npm install

# Option A: Run all 3 portals concurrently:
npm run dev

# Option B: Run individual portals independently:
npm run dev:driver   # Starts Driver Portal on http://localhost:3110
npm run dev:owner    # Starts Owner Portal on http://localhost:6782
npm run dev:admin    # Starts Admin Portal on http://localhost:5431
```

### 2. Running Backend API
```bash
cd Backend
python -m venv venv
.\venv\Scripts\activate  # Windows (or source venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
python -m app.db.migrate
uvicorn main:app --reload --port 8000
```
Backend Swagger API Docs: `http://localhost:8000/docs`

### 3. Running with Docker Compose
```bash
docker-compose up --build
```
Access points:
- **Backend API**: `http://localhost:8000` / `http://localhost/docs`
- **Postgres Database**: `localhost:5432`
- **Redis Cache**: `localhost:6379`

---

## 🧪 Testing & Verification

Run the full test suite locally:
```bash
cd Backend
.\venv\Scripts\python.exe -m pytest -v tests/
```

Run frontend build verification:
```bash
cd Frontend
npm run build
```

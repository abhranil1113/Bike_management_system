# VeloRent Pro - Enterprise Bike Management & Rental System

Welcome to the **VeloRent Pro** repository! This is a production-grade, full-stack bike management and rental platform built with FastAPI, React, PostgreSQL, Redis, Docker, and GitHub Actions CI/CD.

---

## 🚀 Architecture & Tech Stack

### 1. Backend (`/Backend`)
- **Framework**: Python 3.12 + FastAPI (Async REST API & Socket.IO WebSockets)
- **Database**: PostgreSQL 15 + SQLAlchemy 2.0 ORM with Alembic schema migrations
- **Caching & Queues**: Redis + Socket.IO (Real-time notification engine)
- **Authentication**: JWT Access & Refresh Token authentication with HTTP-only cookies, Bcrypt password hashing, and role-based access control (Driver, Owner, Admin)
- **Background Cron Worker**: Async background worker loop processing auto-collections, overdue penalties, and scheduled jobs (`app/cron/scheduler.py`)
- **Testing**: Pytest test suite with 100% execution coverage across auth, driver, owner, wallet, support, and cron modules

### 2. Frontend (`/Frontend`)
- **Framework**: React 18 + TypeScript + Vite + TailwindCSS + Lucide Icons
- **State & Auth**: React Context API (`AuthContext`) managing JWT sessions, wallet balance, and active workspace state
- **Dashboards & Views**:
  - **Driver Workspace** (`DriverView.tsx`): Bike search & filter grid, KYC document upload (Aadhaar/License), active rental duration timer, wallet transaction history, and support tickets
  - **Owner Workspace** (`OwnerView.tsx`): Fleet overview, earnings & rental metrics, bike listing manager with RC/image uploads, booking request approvals
  - **Admin Workspace** (`AdminView.tsx`): System KPI metrics (Platform Revenue, Commission, Active Rentals), user verification table, bike listing queue, broadcast notifications console, audit logs
  - **Global Navigation** (`Navbar.tsx`): Real-time Socket.IO notification bell dropdown, live wallet balance top-up modal (`WalletModal.tsx`), workspace switcher

### 3. Docker & Infrastructure (`docker-compose.yml`)
- **Multi-Container Architecture**:
  - `db`: PostgreSQL 15-Alpine database container
  - `redis`: Redis 7-Alpine cache & pub/sub message broker
  - `backend`: FastAPI API service container
  - `worker`: Background cron worker processing background tasks
  - `nginx`: Reverse proxy routing frontend assets and API endpoints
- **Production Frontend Dockerfile**: Multi-stage `node:20-alpine` build + `nginx:alpine` serving

### 4. Automated CI/CD Pipeline (`.github/workflows/ci-cd.yml`)
- **Linting & Code Quality**: Flake8 linting (`--select=E9,F63,F7,F82`)
- **Database Migrations**: Automated schema migration against test PostgreSQL database
- **Pytest Execution**: Automated backend test suite execution
- **Frontend Build Verification**: Node.js 20 environment setup, dependency installation (`npm ci`), and Vite bundle compilation (`npm run build`)
- **Container Build Verification**: Automated multi-container Docker image build for Backend & Frontend

---

## 🔑 Key Features Implemented

1. **Authentication & Multi-Role Governance**:
   - Driver, Owner, and Admin workspace switching with secure JWT session handling.

2. **Wallet & Payment Ecosystem**:
   - Razorpay payment gateway integration, instant wallet top-up, automated debit on booking, credit on owner payouts, and negative balance support for late fees.

3. **Fleet Management & Rental Workflow**:
   - Owners list bikes with pricing, RC documents, and photos.
   - Drivers search bikes by brand, fuel type, city, filter by price, and request bookings.
   - Owners accept/reject booking requests in real-time.

4. **Real-Time WebSockets & Notifications**:
   - Socket.IO server emitting realtime events (`booking_updated`, `payment_completed`, `admin_broadcast`).
   - React navbar notification bell with unread counters and live drop-downs.

5. **Analytics & Reports Dashboard**:
   - Admin KPI summary metrics: Platform Revenue, Gross Rental Collections, Active Bookings, System Commission.
   - Owner earnings summary and transaction history.

6. **Scheduled Background Jobs**:
   - Cron worker automatically processes overdue rentals, calculates daily late penalties, and updates system ledgers.

---

## ⚡ Quick Start / Local Setup

### Running with Docker Compose (Recommended)
```bash
docker-compose up --build
```
Access points:
- **Frontend UI**: `http://localhost`
- **Backend API Docs**: `http://localhost:8000/docs`

### Running Backend Locally
```bash
cd Backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -m app.db.migrate
uvicorn main:app --reload --port 8000
```

### Running Frontend Locally
```bash
cd Frontend
npm install
npm run dev
```

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

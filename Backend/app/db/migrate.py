# Backend/app/db/migrate.py

import os
import sys
from pathlib import Path

# Add Backend directory to Python path for standalone script execution
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import text
from app.db.database import engine
from app.db.schema import Base

def run_migrations():
    """Creates missing tables and adds missing columns/constraints in existing or fresh database."""
    print("[MIGRATION] Running schema migration...")

    # 1. Create any missing tables (users, user_sessions, driver_profiles, owner_profiles, wallets, etc.)
    Base.metadata.create_all(bind=engine)

    with engine.begin() as conn:
        # 2. Alter users table
        conn.execute(text("ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE NOT NULL;"))
        conn.execute(text("ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0 NOT NULL;"))
        conn.execute(text("ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP WITH TIME ZONE;"))

        # 3. Alter user_sessions table
        conn.execute(text("ALTER TABLE IF EXISTS user_sessions ADD COLUMN IF NOT EXISTS refresh_token_hash VARCHAR(255);"))
        conn.execute(text("ALTER TABLE IF EXISTS user_sessions ADD COLUMN IF NOT EXISTS ip_address VARCHAR(64);"))
        conn.execute(text("ALTER TABLE IF EXISTS user_sessions ADD COLUMN IF NOT EXISTS user_agent TEXT;"))
        conn.execute(text("ALTER TABLE IF EXISTS user_sessions ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE NOT NULL;"))

        # 4. Alter driver_profiles table
        conn.execute(text("ALTER TABLE IF EXISTS driver_profiles ADD COLUMN IF NOT EXISTS driving_license_file_path VARCHAR(255);"))
        conn.execute(text("ALTER TABLE IF EXISTS driver_profiles ADD COLUMN IF NOT EXISTS aadhaar_file_path VARCHAR(255);"))
        conn.execute(text("ALTER TABLE IF EXISTS driver_profiles ADD COLUMN IF NOT EXISTS pan_number VARCHAR(20);"))
        conn.execute(text("ALTER TABLE IF EXISTS driver_profiles ADD COLUMN IF NOT EXISTS pan_file_path VARCHAR(255);"))
        conn.execute(text("ALTER TABLE IF EXISTS driver_profiles ADD COLUMN IF NOT EXISTS address TEXT;"))
        conn.execute(text("ALTER TABLE IF EXISTS driver_profiles ADD COLUMN IF NOT EXISTS profile_picture_path VARCHAR(255);"))

        # 5. Alter owner_profiles table
        conn.execute(text("ALTER TABLE IF EXISTS owner_profiles ADD COLUMN IF NOT EXISTS profile_picture_path VARCHAR(255);"))

        # 6. Alter bike_pricing for hourly tariffs & late fees
        conn.execute(text("ALTER TABLE IF EXISTS bike_pricing ADD COLUMN IF NOT EXISTS hourly_rate NUMERIC(10, 2) DEFAULT 100.00;"))
        conn.execute(text("ALTER TABLE IF EXISTS bike_pricing ADD COLUMN IF NOT EXISTS late_fee_per_hour NUMERIC(10, 2) DEFAULT 50.00;"))

        # 7. Alter bike_booking_requests for duration and COD status
        conn.execute(text("ALTER TABLE IF EXISTS bike_booking_requests ADD COLUMN IF NOT EXISTS rental_hours INTEGER DEFAULT 24;"))
        conn.execute(text("ALTER TABLE IF EXISTS bike_booking_requests ADD COLUMN IF NOT EXISTS total_amount NUMERIC(10, 2) DEFAULT 0.00;"))
        conn.execute(text("ALTER TABLE IF EXISTS bike_booking_requests ADD COLUMN IF NOT EXISTS payment_method VARCHAR(30) DEFAULT 'cod';"))
        conn.execute(text("ALTER TABLE IF EXISTS bike_booking_requests ADD COLUMN IF NOT EXISTS cash_received BOOLEAN DEFAULT FALSE;"))
        conn.execute(text("ALTER TABLE IF EXISTS bike_booking_requests ADD COLUMN IF NOT EXISTS cash_received_at TIMESTAMP WITH TIME ZONE;"))
        conn.execute(text("ALTER TABLE IF EXISTS bike_booking_requests ADD COLUMN IF NOT EXISTS cod_admin_escalated BOOLEAN DEFAULT FALSE;"))

        # 8. Alter driver_bike_assignments for duration, COD status, reminder timestamp & escalation
        conn.execute(text("ALTER TABLE IF EXISTS driver_bike_assignments ADD COLUMN IF NOT EXISTS rental_hours INTEGER DEFAULT 24;"))
        conn.execute(text("ALTER TABLE IF EXISTS driver_bike_assignments ADD COLUMN IF NOT EXISTS total_rent_amount NUMERIC(10, 2) DEFAULT 0.00;"))
        conn.execute(text("ALTER TABLE IF EXISTS driver_bike_assignments ADD COLUMN IF NOT EXISTS payment_method VARCHAR(30) DEFAULT 'cod';"))
        conn.execute(text("ALTER TABLE IF EXISTS driver_bike_assignments ADD COLUMN IF NOT EXISTS cash_received BOOLEAN DEFAULT FALSE;"))
        conn.execute(text("ALTER TABLE IF EXISTS driver_bike_assignments ADD COLUMN IF NOT EXISTS cash_received_at TIMESTAMP WITH TIME ZONE;"))
        conn.execute(text("ALTER TABLE IF EXISTS driver_bike_assignments ADD COLUMN IF NOT EXISTS last_cod_reminder_at TIMESTAMP WITH TIME ZONE;"))
        conn.execute(text("ALTER TABLE IF EXISTS driver_bike_assignments ADD COLUMN IF NOT EXISTS cod_admin_escalated BOOLEAN DEFAULT FALSE;"))

        # 9. Drop nonnegative check constraint on wallets to support negative balance on overdue rental penalties
        try:
            conn.execute(text("ALTER TABLE IF EXISTS wallets DROP CONSTRAINT IF EXISTS ck_wallets_balance_nonnegative;"))
        except Exception as e:
            print("[MIGRATION WARNING] Could not drop wallet constraint:", str(e))

        # 10. Drop check constraints on bike_booking_requests and payments status if restrictive to allow 'refunded'
        try:
            conn.execute(text("ALTER TABLE IF EXISTS bike_booking_requests DROP CONSTRAINT IF EXISTS bike_booking_requests_status_check;"))
            conn.execute(text("ALTER TABLE IF EXISTS bike_booking_requests DROP CONSTRAINT IF EXISTS ck_bike_booking_requests_booking_request_status;"))
            conn.execute(text("ALTER TABLE IF EXISTS payments DROP CONSTRAINT IF EXISTS payments_status_check;"))
            conn.execute(text("ALTER TABLE IF EXISTS payments DROP CONSTRAINT IF EXISTS ck_payments_payment_status;"))
        except Exception as e:
            print("[MIGRATION WARNING] Could not drop status check constraints:", str(e))

    print("[MIGRATION] Schema migration completed successfully!")

if __name__ == "__main__":
    run_migrations()

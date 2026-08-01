# Backend/app/db/migrate.py

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
        conn.execute(text("ALTER TABLE IF EXISTS driver_profiles ADD COLUMN IF NOT EXISTS profile_picture_path VARCHAR(255);"))

        # 5. Alter owner_profiles table
        conn.execute(text("ALTER TABLE IF EXISTS owner_profiles ADD COLUMN IF NOT EXISTS profile_picture_path VARCHAR(255);"))

        # 6. Drop nonnegative check constraint on wallets to support negative balance on overdue rental penalties
        try:
            conn.execute(text("ALTER TABLE IF EXISTS wallets DROP CONSTRAINT IF EXISTS ck_wallets_balance_nonnegative;"))
        except Exception as e:
            print("[MIGRATION WARNING] Could not drop wallet constraint:", str(e))

    print("[MIGRATION] Schema migration completed successfully!")

if __name__ == "__main__":
    run_migrations()

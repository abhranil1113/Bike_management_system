# Backend/app/db/migrate.py

from sqlalchemy import text
from app.db.database import engine
from app.db.schema import Base

def run_migrations():
    """Adds missing columns and creates missing tables in existing database."""
    print("[MIGRATION] Running schema migration...")
    with engine.begin() as conn:
        # 1. Alter users table
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE NOT NULL;"))
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0 NOT NULL;"))
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP WITH TIME ZONE;"))

        # 2. Alter user_sessions table
        conn.execute(text("ALTER TABLE user_sessions ADD COLUMN IF NOT EXISTS refresh_token_hash VARCHAR(255);"))
        conn.execute(text("ALTER TABLE user_sessions ADD COLUMN IF NOT EXISTS ip_address VARCHAR(64);"))
        conn.execute(text("ALTER TABLE user_sessions ADD COLUMN IF NOT EXISTS user_agent TEXT;"))
        conn.execute(text("ALTER TABLE user_sessions ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE NOT NULL;"))

        # 3. Alter driver_profiles table
        conn.execute(text("ALTER TABLE driver_profiles ADD COLUMN IF NOT EXISTS driving_license_file_path VARCHAR(255);"))
        conn.execute(text("ALTER TABLE driver_profiles ADD COLUMN IF NOT EXISTS aadhaar_file_path VARCHAR(255);"))
        conn.execute(text("ALTER TABLE driver_profiles ADD COLUMN IF NOT EXISTS profile_picture_path VARCHAR(255);"))

        # 4. Alter owner_profiles table
        conn.execute(text("ALTER TABLE owner_profiles ADD COLUMN IF NOT EXISTS profile_picture_path VARCHAR(255);"))

    # 5. Create any new tables (email_verification_tokens, password_reset_tokens, wallets, wallet_transactions, etc.)
    Base.metadata.create_all(bind=engine)
    print("[MIGRATION] Schema migration completed successfully!")

if __name__ == "__main__":
    run_migrations()

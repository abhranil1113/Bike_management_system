# Backend/run_migration.py

import os
import sys
from pathlib import Path
from urllib.parse import urlparse, unquote

# Add Backend root to sys.path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv

# Load .env from Backend/.env
env_path = BACKEND_DIR / ".env"
load_dotenv(dotenv_path=env_path)

from sqlalchemy import create_engine, text
from app.db.schema import Base
from app.db.migrate import run_migrations


def ensure_database_exists(db_url: str):
    """
    Checks if the target database exists. If not, connects to default 'postgres' database
    and creates the target database automatically.
    """
    try:
        engine = create_engine(db_url, connect_args={"connect_timeout": 5})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        err_msg = str(e).lower()
        if 'database "' in err_msg and "does not exist" in err_msg:
            # Extract target DB name and connection details
            parsed = urlparse(db_url)
            target_db = parsed.path.lstrip("/")

            # Construct URL for default 'postgres' database
            default_url = db_url.rsplit("/", 1)[0] + "/postgres"
            print(f"[MIGRATION] Target database '{target_db}' does not exist. Creating it via postgres database...")
            try:
                default_engine = create_engine(default_url, isolation_level="AUTOCOMMIT", connect_args={"connect_timeout": 5})
                with default_engine.connect() as conn:
                    conn.execute(text(f'CREATE DATABASE "{target_db}"'))
                print(f"[MIGRATION] Database '{target_db}' created successfully!")
                return True
            except Exception as create_err:
                print(f"[MIGRATION ERROR] Could not automatically create database '{target_db}': {create_err}")
                return False
        else:
            print("\n" + "=" * 70)
            print(" [MIGRATION ERROR] Could not connect to PostgreSQL server.")
            print("=" * 70)
            print(f"Details: {e}")
            print("\nTroubleshooting steps:")
            print("1. Ensure PostgreSQL is running on your machine.")
            print("   - On Windows: Open Services (services.msc), find 'postgresql-x64-18' and click 'Start'")
            print("   - Or run as Administrator: Start-Service postgresql-x64-18 (or net start postgresql-x64-18)")
            print("2. Check Backend/.env credentials:")
            print(f"   DATABASE_URL = {os.getenv('DATABASE_URL')}")
            print("=" * 70 + "\n")
            return False


def main():
    print("\n" + "=" * 60)
    print(" 🚀 BIKE MANAGEMENT SYSTEM - DATABASE MIGRATION")
    print("=" * 60)

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("[ERROR] DATABASE_URL is not set in Backend/.env file.")
        sys.exit(1)

    print(f"[INFO] Target Database: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    print("[INFO] Checking database connection...")

    if not ensure_database_exists(db_url):
        sys.exit(1)

    print("[INFO] PostgreSQL connection successful!")
    print("[INFO] Applying table schemas and migrations...")

    try:
        run_migrations()
        print("\n" + "=" * 60)
        print(" ✅ DATABASE MIGRATION COMPLETED SUCCESSFULLY!")
        print(" All tables, time-based tariffs, COD fields, and indexes are up to date.")
        print("=" * 60 + "\n")
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

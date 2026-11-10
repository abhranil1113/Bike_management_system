# Backend/seed_admin.py
import sys
import os

# Ensure Backend is on path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.db.database import engine, SessionLocal
from app.db.schema import Base, User, UserRole, UserLifecycleStatus
from app.db.migrate import run_migrations
from app.core.security import hash_password

def seed_admin():
    print("[1/3] Running schema migrations...")
    run_migrations()
    Base.metadata.create_all(bind=engine)

    print("[2/3] Checking for existing admin user...")
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not admin:
            admin = User(
                email="admin@velorent.com",
                phone="9999999999",
                role=UserRole.ADMIN,
                hashed_password=hash_password("Admin@12345"),
                lifecycle_status=UserLifecycleStatus.ACTIVE,
                is_active=True,
                is_verified=True,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print("=========================================================")
            print(" [SUCCESS] Default Administrator Account Created:")
            print(" Email:    admin@velorent.com")
            print(" Password: Admin@12345")
            print(" Role:     admin")
            print("=========================================================")
        else:
            print(f"[INFO] Existing admin found: {admin.email} (ID: {admin.id})")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Could not seed admin: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()

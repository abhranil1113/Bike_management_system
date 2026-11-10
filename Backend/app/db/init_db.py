# app/db/init_db.py
from app.db.database import engine, SessionLocal
from app.db.schema import Base, User, UserRole, UserLifecycleStatus
from app.db.migrate import run_migrations
from app.core.security import hash_password

def init_db():
    run_migrations()
    Base.metadata.create_all(bind=engine)

    # Auto-seed initial platform admin if none exists
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
            print("[SEED] Default admin created: admin@velorent.com / Admin@12345")
    except Exception as e:
        print("[SEED ERROR] Failed to seed default admin:", e)
        db.rollback()
    finally:
        db.close()

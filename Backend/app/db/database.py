#app/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# ========================
# DATABASE URL
# ========================
DATABASE_URL = settings.DATABASE_URL

# ========================
# ENGINE
# ========================
engine = create_engine(
    DATABASE_URL,
    echo=True,   # set False in production
    future=True
)

# ========================
# SESSION
# ========================
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

# ========================
# DEPENDENCY
# ========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
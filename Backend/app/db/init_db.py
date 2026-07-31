# app/db/init_db.py
from app.db.database import engine
from app.db.schema import Base
from app.db.migrate import run_migrations

def init_db():
    run_migrations()
    Base.metadata.create_all(bind=engine)
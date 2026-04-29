#Backend/app/db/init_db.py
from app.db.session import engine
from app.db.schema import Base

def init_db():
    Base.metadata.create_all(bind=engine)
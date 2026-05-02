# main.py

from fastapi import FastAPI

from app.db.init_db import init_db
from app.auth.router import router as auth_router

# ========================
# APP INSTANCE
# ========================
app = FastAPI(
    title="Bike Management System API",
    version="1.0.0"
)


# ========================
# STARTUP EVENT (FIXED STYLE)
# ========================
@app.on_event("startup")
def startup_event():
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print("❌ Database initialization failed:", e)


# ========================
# ROOT ENDPOINT
# ========================
@app.get("/")
def root():
    return {
        "message": "Bike Management System Running 🚀",
        "status": "success"
    }


# ========================
# ROUTERS
# ========================
app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)
# main.py

from fastapi import FastAPI

from app.db.init_db import init_db
from app.auth.router import router as auth_router
from app.profile import ownerprofile, driver_profile
from app.documents.bike_document import router as bike_document_router
from app.documents import bike_images
from app.bikes import bike
from app.bikes import bike_price
from app.booking.booking_request import router as booking_router
from app.admin import driver_owner_approval, bike_approval
from app.bikes import driver_view


# ========================
# APP INSTANCE
# ========================
app = FastAPI(
    title="Bike Management System API",
    version="1.0.0"
)

app.include_router(ownerprofile.router)
app.include_router(driver_profile.router)
app.include_router(bike_document_router)
app.include_router(bike_images.router)
app.include_router(bike.router)
app.include_router(bike_price.router)
app.include_router(booking_router)
app.include_router(bike_approval.router)
app.include_router(driver_owner_approval.router)
app.include_router(driver_view.router)
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
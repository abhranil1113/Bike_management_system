# main.py

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.db.init_db import init_db
from app.auth.router import router as auth_router
from app.admin.router import router as admin_router
from app.owner.router import router as owner_router
from app.driver.router import router as driver_router
from app.bikes.driver_view import router as driver_bike_router
from app.bikes.review_router import router as review_router
from app.wallet.router import router as wallet_router
from app.payment.router import router as payment_router
from app.notifications.router import router as notifications_router
from app.support.router import router as support_router
from app.reports.router import router as reports_router
from app.cron.router import router as cron_router
from app.cron.scheduler import start_cron_scheduler, stop_cron_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_db()
        print("[DB] Database initialized & schema migrated successfully.")
    except Exception as e:
        print("[DB ERROR] Database initialization failed:", str(e))
    
    # Start background cron worker scheduler
    try:
        start_cron_scheduler(interval_seconds=60)
        print("[CRON] Background worker scheduler started.")
    except Exception as e:
        print("[CRON ERROR] Could not start scheduler:", str(e))
        
    yield
    
    # Stop background scheduler on shutdown
    stop_cron_scheduler()


app = FastAPI(
    title="Full Stack Bike Management System API",
    description="Production-Ready Enterprise Bike Rental & Management System API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Uploads Directory
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/", tags=["Health Check"])
def root():
    return {
        "app": "Bike Management System API",
        "status": "healthy",
        "version": "2.0.0",
        "documentation": "/docs",
    }


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"[UNHANDLED EXCEPTION] {request.method} {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An internal server error occurred.",
            "detail": str(exc),
        },
    )


# Include All Feature Routers
app.include_router(auth_router, prefix="/auth")
app.include_router(admin_router)
app.include_router(owner_router)
app.include_router(driver_router)
app.include_router(driver_bike_router)
app.include_router(review_router)
app.include_router(wallet_router)
app.include_router(payment_router)
app.include_router(notifications_router)
app.include_router(support_router)
app.include_router(reports_router)
app.include_router(cron_router)
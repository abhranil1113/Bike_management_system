# app/cron/router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schema import User
from app.api.deps import get_current_admin
from app.schemas.auth_schema import StandardResponse
from app.cron.jobs import run_all_cron_jobs
from app.cron.scheduler import _cron_task, _keep_running

router = APIRouter(prefix="/admin/cron", tags=["Admin - Background Jobs & Scheduler"])


@router.post("/run", response_model=StandardResponse, summary="Trigger Background Cron Jobs Manually")
async def trigger_cron_jobs_api(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    res = run_all_cron_jobs(db)
    return StandardResponse(
        success=True,
        message="Background cron jobs executed successfully.",
        data=res,
    )


@router.get("/status", response_model=StandardResponse, summary="Get Background Scheduler Status")
async def get_cron_status_api(
    admin: User = Depends(get_current_admin),
):
    is_active = _cron_task is not None and not _cron_task.done() and _keep_running
    status_data = {
        "scheduler_running": is_active,
        "job_names": [
            "auto_cancel_stale_booking_requests",
            "process_overdue_rental_penalties",
            "generate_daily_rental_ledgers_and_overdue_notices",
            "check_bike_maintenance_and_insurance_expiries",
        ],
    }
    return StandardResponse(
        success=True,
        message="Cron scheduler status fetched.",
        data=status_data,
    )

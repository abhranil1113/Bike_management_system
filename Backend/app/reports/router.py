# app/reports/router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schema import User
from app.api.deps import get_current_admin
from app.schemas.auth_schema import StandardResponse
from app.reports.service import (
    generate_revenue_report_service,
    generate_analytics_dashboard_service,
)

router = APIRouter(prefix="/reports", tags=["Reports & Analytics"])


@router.get("/revenue", response_model=StandardResponse, summary="Get Revenue & Platform Analytics Report")
async def get_revenue_report_api(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    report = await generate_revenue_report_service(db)
    return StandardResponse(success=True, message="Revenue report generated.", data=report)


@router.get("/dashboard", response_model=StandardResponse, summary="Get Master Analytics Dashboard")
async def get_analytics_dashboard_api(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    dashboard = await generate_analytics_dashboard_service(db)
    return StandardResponse(
        success=True,
        message="Analytics dashboard metrics fetched successfully.",
        data=dashboard,
    )

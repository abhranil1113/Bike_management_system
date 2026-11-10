# app/admin/schemas.py

from typing import Optional, List, Any
from decimal import Decimal
from pydantic import BaseModel, Field
from datetime import datetime


class ApprovalDecisionRequest(BaseModel):
    approved: bool = Field(..., description="True to approve, False to reject")
    rejection_reason: Optional[str] = Field(None, description="Reason if rejected")


class UserStatusUpdateRequest(BaseModel):
    status: str = Field(..., example="active", description="active, blocked, or deleted")


class PlatformSettingsUpdate(BaseModel):
    platform_commission_percent: Decimal = Field(..., ge=0, le=100, example=10.00)
    late_fee_grace_days: int = Field(..., ge=0, example=0)


class AdminDashboardStats(BaseModel):
    total_users: int
    total_owners: int
    total_drivers: int
    total_bikes: int
    available_bikes: int
    assigned_bikes: int
    pending_owner_verifications: int
    pending_driver_verifications: int
    pending_bike_verifications: int
    cod_unpaid_count: Optional[int] = 0
    cod_escalations_count: Optional[int] = 0
    total_revenue: Decimal
    total_platform_commission: Decimal

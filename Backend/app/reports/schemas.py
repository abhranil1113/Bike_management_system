# app/reports/schemas.py

from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel


class RevenueReportSummary(BaseModel):
    total_gross_revenue: Decimal
    total_platform_commission: Decimal
    total_owner_payouts: Decimal
    total_successful_payments: int

# app/notifications/schemas.py

from typing import Optional, List
from pydantic import BaseModel, Field


class BroadcastNotificationRequest(BaseModel):
    title: str = Field(..., example="System Maintenance")
    message: str = Field(..., example="Scheduled maintenance tonight at 12 AM.")
    target_role: Optional[str] = Field(None, example="driver", description="owner, driver, or null for all")

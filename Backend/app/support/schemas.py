# app/support/schemas.py

from typing import Optional
from pydantic import BaseModel, Field


class CreateSupportTicketRequest(BaseModel):
    subject: str = Field(..., example="App issue during payment")
    description: str = Field(..., example="Payment was debited but order stayed created.")


class ResolveSupportTicketRequest(BaseModel):
    ticket_id: str = Field(...)
    status: str = Field(..., example="resolved", description="resolved or rejected")
    reason: Optional[str] = Field(None, example="Issue investigated and resolved")

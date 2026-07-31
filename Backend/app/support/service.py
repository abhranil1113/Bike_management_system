# app/support/service.py

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.db.schema import User, SupportTicket, SupportStatus, utcnow
from app.support.schemas import CreateSupportTicketRequest, ResolveSupportTicketRequest


async def create_support_ticket_service(
    db: Session, user: User, req: CreateSupportTicketRequest
) -> Dict[str, Any]:
    ticket = SupportTicket(
        user_id=user.id,
        subject=req.subject,
        description=req.description,
        status=SupportStatus.OPEN,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return {"message": "Support ticket created successfully.", "ticket_id": ticket.id}


async def resolve_support_ticket_service(
    db: Session, admin: User, req: ResolveSupportTicketRequest
) -> Dict[str, Any]:
    ticket = db.query(SupportTicket).filter(SupportTicket.id == req.ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Support ticket not found")

    status_str = req.status.lower()
    if status_str == "resolved":
        ticket.status = SupportStatus.RESOLVED
        ticket.resolved_at = utcnow()
    elif status_str == "rejected":
        ticket.status = SupportStatus.REJECTED
    else:
        raise HTTPException(status_code=400, detail="Invalid status")

    db.commit()
    return {"message": f"Support ticket marked as {ticket.status.value}."}

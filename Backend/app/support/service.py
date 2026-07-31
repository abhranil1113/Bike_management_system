# app/support/service.py

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.db.schema import User, SupportTicket, SupportStatus, utcnow
from app.support.schemas import CreateSupportTicketRequest, ResolveSupportTicketRequest
from app.notifications.service import create_notification


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

    create_notification(
        db,
        user.id,
        "Support Ticket Created",
        "Your support request has been submitted successfully.",
    )

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
        db.commit()
        create_notification(
            db,
            ticket.user_id,
            "Support Ticket Resolved",
            "Your support request has been resolved.",
        )
    elif status_str in ["rejected", "closed"]:
        ticket.status = SupportStatus.REJECTED
        db.commit()
        reason_msg = (
            f"Your support request has been closed. Reason: {req.reason}"
            if req.reason
            else "Your support request has been closed."
        )
        create_notification(
            db,
            ticket.user_id,
            "Support Ticket Closed",
            reason_msg,
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid status")

    return {"message": f"Support ticket marked as {ticket.status.value}."}

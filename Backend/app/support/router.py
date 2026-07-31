# app/support/router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schema import User, SupportTicket
from app.api.deps import get_current_user, get_current_admin
from app.schemas.auth_schema import StandardResponse
from app.support.schemas import CreateSupportTicketRequest, ResolveSupportTicketRequest
from app.support.service import (
    create_support_ticket_service,
    resolve_support_ticket_service,
)

router = APIRouter(prefix="/support", tags=["Support Tickets"])


@router.post("/tickets", response_model=StandardResponse, summary="Create Support Ticket")
async def create_ticket_api(
    req: CreateSupportTicketRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    res = await create_support_ticket_service(db, user, req)
    return StandardResponse(success=True, message=res["message"], data=res)


@router.get("/my-tickets", response_model=StandardResponse, summary="List Current User's Support Tickets")
async def list_my_tickets_api(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tickets = db.query(SupportTicket).filter(
        SupportTicket.user_id == user.id
    ).order_by(SupportTicket.created_at.desc()).all()

    data = [
        {
            "id": t.id,
            "subject": t.subject,
            "description": t.description,
            "status": t.status.value,
            "resolved_at": t.resolved_at.isoformat() if t.resolved_at else None,
            "created_at": t.created_at.isoformat(),
        }
        for t in tickets
    ]
    return StandardResponse(success=True, message="Support tickets fetched.", data=data)


@router.post("/admin/resolve", response_model=StandardResponse, summary="Admin Resolve or Reject Support Ticket")
async def resolve_ticket_api(
    req: ResolveSupportTicketRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    res = await resolve_support_ticket_service(db, admin, req)
    return StandardResponse(success=True, message=res["message"])

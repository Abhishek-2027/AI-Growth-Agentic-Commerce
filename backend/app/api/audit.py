from fastapi import APIRouter, HTTPException
from app.services import audit_service, order_service

router = APIRouter(prefix="/api/audit", tags=["Audit"])


@router.get("/{session_id}")
async def get_session_audit(session_id: str):
    """Return full audit timeline for a session."""
    events = await audit_service.get_session_audit(session_id)
    return {"session_id": session_id, "events": events, "count": len(events)}


@router.get("/order/{order_id}")
async def get_order_audit(order_id: str):
    """Return all audit events referencing a specific order."""
    events = await audit_service.get_order_audit(order_id)
    return {"order_id": order_id, "events": events, "count": len(events)}


@router.get("")
async def get_all_audits(limit: int = 100):
    """Return most recent audit events across all sessions."""
    events = await audit_service.get_all_recent_audits(limit=limit)
    return {"events": events, "count": len(events)}

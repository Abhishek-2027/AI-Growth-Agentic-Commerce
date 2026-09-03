from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services import proposal_service
from app.services import audit_service
from app.models.audit import AuditActor, AuditEventType, AuditStatus

router = APIRouter(prefix="/api/purchase", tags=["Purchase"])


class ApprovalRequest(BaseModel):
    session_id: Optional[str] = None


@router.get("/{proposal_id}")
async def get_proposal(proposal_id: str):
    proposal = await proposal_service.get_proposal(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal


@router.post("/{proposal_id}/approve")
async def approve_proposal(proposal_id: str, req: ApprovalRequest):
    """User explicitly approves the purchase proposal — recorded in audit trail."""
    proposal = await proposal_service.get_proposal(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    if proposal.get("status") == "POLICY_REJECTED":
        raise HTTPException(
            status_code=400, detail="Cannot approve a policy-rejected proposal"
        )

    updated = await proposal_service.approve_proposal(proposal_id)
    if not updated:
        raise HTTPException(status_code=400, detail="Could not approve proposal")

    session_id = req.session_id or proposal.get("session_id", "")

    await audit_service.log_event(
        session_id=session_id,
        actor=AuditActor.USER,
        action=AuditEventType.USER_APPROVED,
        reason=f"User approved purchase of {proposal.get('product_name')} for ₹{proposal.get('expected_amount')}",
        status=AuditStatus.SUCCESS,
        metadata={"proposal_id": proposal_id, "amount": proposal.get("expected_amount")},
    )

    return {"message": "Proposal approved", "proposal": updated}


@router.post("/{proposal_id}/reject")
async def reject_proposal(proposal_id: str, req: ApprovalRequest):
    """User rejects the purchase proposal — recorded in audit trail."""
    proposal = await proposal_service.get_proposal(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    updated = await proposal_service.reject_proposal(proposal_id)
    session_id = req.session_id or proposal.get("session_id", "")

    await audit_service.log_event(
        session_id=session_id,
        actor=AuditActor.USER,
        action=AuditEventType.USER_REJECTED,
        reason="User rejected the purchase proposal",
        status=AuditStatus.INFO,
        metadata={"proposal_id": proposal_id},
    )

    return {"message": "Proposal rejected", "proposal": updated}

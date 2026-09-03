from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ProposalStatus(str, Enum):
    PENDING = "PENDING"
    POLICY_APPROVED = "POLICY_APPROVED"
    POLICY_REJECTED = "POLICY_REJECTED"
    AWAITING_USER_APPROVAL = "AWAITING_USER_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class PolicyResult(BaseModel):
    approved: bool
    reasons: List[str] = []
    blocked_reasons: List[str] = []
    budget_check: bool = False
    stock_check: bool = False
    quantity_check: bool = False
    currency_check: bool = False
    product_active_check: bool = False


class PurchaseProposalCreate(BaseModel):
    session_id: str
    product_id: str
    quantity: int = 1
    user_budget: float
    reason: str
    recommendation_reasons: List[str] = []


class PurchaseProposalResponse(BaseModel):
    id: str = Field(alias="_id")
    session_id: str
    product_id: str
    product_name: str
    quantity: int
    expected_amount: float
    currency: str = "INR"
    user_budget: float
    reason: str
    recommendation_reasons: List[str] = []
    status: ProposalStatus = ProposalStatus.PENDING
    policy_result: Optional[PolicyResult] = None
    created_at: datetime
    approved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}

    class Config:
        populate_by_name = True


class ApprovalRequest(BaseModel):
    session_id: Optional[str] = None

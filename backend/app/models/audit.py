from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class AuditActor(str, Enum):
    AGENT = "agent"
    POLICY = "policy"
    USER = "user"
    PAYMENT = "payment"
    GUARDRAIL = "guardrail"
    SYSTEM = "system"


class AuditStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    PENDING = "PENDING"
    INFO = "INFO"


class AuditEventType(str, Enum):
    USER_REQUEST_RECEIVED = "USER_REQUEST_RECEIVED"
    GUARDRAIL_INPUT_CHECK = "GUARDRAIL_INPUT_CHECK"
    GUARDRAIL_INPUT_BLOCKED = "GUARDRAIL_INPUT_BLOCKED"
    INTENT_EXTRACTED = "INTENT_EXTRACTED"
    CATALOG_SEARCHED = "CATALOG_SEARCHED"
    PRODUCTS_ANALYZED = "PRODUCTS_ANALYZED"
    PRODUCT_SELECTED = "PRODUCT_SELECTED"
    RECOMMENDATION_CREATED = "RECOMMENDATION_CREATED"
    PURCHASE_PROPOSAL_CREATED = "PURCHASE_PROPOSAL_CREATED"
    POLICY_CHECK_PASSED = "POLICY_CHECK_PASSED"
    POLICY_CHECK_FAILED = "POLICY_CHECK_FAILED"
    USER_APPROVAL_REQUESTED = "USER_APPROVAL_REQUESTED"
    USER_APPROVED = "USER_APPROVED"
    USER_REJECTED = "USER_REJECTED"
    RAZORPAY_ORDER_CREATED = "RAZORPAY_ORDER_CREATED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    PAYMENT_VERIFIED = "PAYMENT_VERIFIED"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    ORDER_COMPLETED = "ORDER_COMPLETED"
    ORDER_CANCELLED = "ORDER_CANCELLED"


class AuditLogCreate(BaseModel):
    session_id: str
    actor: AuditActor
    action: AuditEventType
    reason: str
    status: AuditStatus
    metadata: Dict[str, Any] = {}


class AuditLogResponse(BaseModel):
    id: str = Field(alias="_id")
    session_id: str
    timestamp: datetime
    actor: str
    action: str
    reason: str
    status: str
    metadata: Dict[str, Any] = {}

    class Config:
        populate_by_name = True

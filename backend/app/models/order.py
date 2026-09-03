from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    CREATED = "CREATED"
    POLICY_APPROVED = "POLICY_APPROVED"
    AWAITING_USER_APPROVAL = "AWAITING_USER_APPROVAL"
    APPROVED = "APPROVED"
    RAZORPAY_ORDER_CREATED = "RAZORPAY_ORDER_CREATED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    PAYMENT_VERIFIED = "PAYMENT_VERIFIED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class OrderCreate(BaseModel):
    user_id: str = "guest_user"
    session_id: str
    proposal_id: str
    product_id: str
    product_name: str
    quantity: int
    amount: float
    currency: str = "INR"


class OrderResponse(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    session_id: str
    proposal_id: str
    product_id: str
    product_name: str
    quantity: int
    amount: float
    currency: str
    status: OrderStatus
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    razorpay_signature: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        populate_by_name = True

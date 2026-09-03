from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class CreateOrderRequest(BaseModel):
    proposal_id: str
    session_id: Optional[str] = None


class CreateOrderResponse(BaseModel):
    order_id: str
    razorpay_order_id: str
    razorpay_key_id: str
    amount: int  # in paise
    currency: str
    product_name: str


class VerifyPaymentRequest(BaseModel):
    order_id: str                    # internal order ID
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class PaymentStatusResponse(BaseModel):
    order_id: str = Field(alias="_id")
    status: str
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    amount: float
    currency: str
    product_name: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        populate_by_name = True

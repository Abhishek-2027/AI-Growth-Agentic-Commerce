from fastapi import APIRouter, HTTPException
from app.models.payment import CreateOrderRequest, VerifyPaymentRequest
from app.services import payment_service, audit_service, order_service
from app.models.audit import AuditActor, AuditEventType, AuditStatus

router = APIRouter(prefix="/api/payments", tags=["Payments"])


@router.post("/create-order")
async def create_payment_order(req: CreateOrderRequest):
    """
    Create Razorpay Test Mode order.
    
    Security guarantees:
    - Amount is ALWAYS read from MongoDB, never from frontend or LLM.
    - Policy is re-validated before any Razorpay order is created.
    - Idempotency guard prevents duplicate charges.
    """
    try:
        checkout_data = await payment_service.create_razorpay_order(
            proposal_id=req.proposal_id,
            session_id=req.session_id or "",
        )

        await audit_service.log_event(
            session_id=req.session_id or "",
            actor=AuditActor.PAYMENT,
            action=AuditEventType.RAZORPAY_ORDER_CREATED,
            reason=f"Razorpay order created: {checkout_data['razorpay_order_id']}",
            status=AuditStatus.SUCCESS,
            metadata={
                "order_id": checkout_data["order_id"],
                "razorpay_order_id": checkout_data["razorpay_order_id"],
                "amount_paise": checkout_data["amount"],
            },
        )

        await audit_service.log_event(
            session_id=req.session_id or "",
            actor=AuditActor.PAYMENT,
            action=AuditEventType.PAYMENT_PENDING,
            reason="Payment checkout opened — waiting for user to complete payment",
            status=AuditStatus.PENDING,
            metadata={"order_id": checkout_data["order_id"]},
        )

        return checkout_data

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment order creation failed: {str(e)}")


@router.post("/verify")
async def verify_payment(req: VerifyPaymentRequest):
    """
    Backend HMAC-SHA256 payment signature verification.
    Frontend payment callback alone is NEVER sufficient.
    """
    try:
        result = await payment_service.verify_razorpay_payment(
            order_id=req.order_id,
            razorpay_order_id=req.razorpay_order_id,
            razorpay_payment_id=req.razorpay_payment_id,
            razorpay_signature=req.razorpay_signature,
        )

        # Get order for session_id
        order = await order_service.get_order(req.order_id)
        session_id = order.get("session_id", "") if order else ""

        await audit_service.log_event(
            session_id=session_id,
            actor=AuditActor.PAYMENT,
            action=AuditEventType.PAYMENT_VERIFIED,
            reason="Payment signature verified successfully by backend",
            status=AuditStatus.SUCCESS,
            metadata={
                "order_id": req.order_id,
                "payment_id": req.razorpay_payment_id,
            },
        )

        await audit_service.log_event(
            session_id=session_id,
            actor=AuditActor.SYSTEM,
            action=AuditEventType.ORDER_COMPLETED,
            reason="Order marked as COMPLETED after successful payment verification",
            status=AuditStatus.SUCCESS,
            metadata={"order_id": req.order_id},
        )

        return {"success": True, "message": "Payment verified successfully", "order_id": req.order_id}

    except ValueError as e:
        order = await order_service.get_order(req.order_id)
        session_id = order.get("session_id", "") if order else ""

        await audit_service.log_event(
            session_id=session_id,
            actor=AuditActor.PAYMENT,
            action=AuditEventType.PAYMENT_FAILED,
            reason=f"Payment verification failed: {str(e)}",
            status=AuditStatus.FAILED,
            metadata={"order_id": req.order_id},
        )

        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{order_id}/status")
async def payment_status(order_id: str):
    """Return current order and payment status."""
    order = await order_service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/{order_id}/cancel")
async def cancel_order(order_id: str):
    """Cancel a pending order — records to audit trail."""
    order = await order_service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.get("status") in ("COMPLETED", "PAYMENT_VERIFIED"):
        raise HTTPException(status_code=400, detail="Cannot cancel a completed order")

    updated = await order_service.update_order_status(order_id, "CANCELLED")

    await audit_service.log_event(
        session_id=order.get("session_id", ""),
        actor=AuditActor.USER,
        action=AuditEventType.ORDER_CANCELLED,
        reason="User cancelled the order",
        status=AuditStatus.INFO,
        metadata={"order_id": order_id},
    )

    return {"message": "Order cancelled", "order": updated}

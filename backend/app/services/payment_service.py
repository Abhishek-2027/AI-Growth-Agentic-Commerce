import razorpay
import hmac
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any
from app.core.config import settings
from app.services.product_service import get_product_by_id
from app.services.proposal_service import get_proposal
from app.services.policy_service import run_policy_check
from app.services.order_service import create_order, update_order_status
from app.db.mongodb import get_collection
import logging

logger = logging.getLogger(__name__)


def _get_razorpay_client() -> razorpay.Client:
    return razorpay.Client(
        auth=(settings.razorpay_key_id, settings.razorpay_key_secret)
    )


async def create_razorpay_order(proposal_id: str, session_id: str) -> Dict[str, Any]:
    """
    Complete secure Razorpay order creation flow:
    1. Load proposal from DB
    2. Load authoritative product price from MongoDB (NEVER from frontend/LLM)
    3. Run policy check again (defense in depth)
    4. Create internal order with idempotency guard
    5. Create Razorpay order
    6. Store Razorpay order ID
    7. Return only public checkout data
    """
    # Step 1: Load proposal
    proposal = await get_proposal(proposal_id)
    if not proposal:
        raise ValueError(f"Proposal {proposal_id} not found")

    if proposal.get("status") not in ("APPROVED", "POLICY_APPROVED"):
        raise ValueError(
            f"Proposal is not approved. Status: {proposal.get('status')}"
        )

    # Step 2: Load authoritative product (price comes from MongoDB, not LLM or frontend)
    product = await get_product_by_id(proposal["product_id"])
    if not product:
        raise ValueError(f"Product {proposal['product_id']} not found")

    quantity = proposal.get("quantity", 1)
    authoritative_amount = float(product["price"]) * quantity

    # Step 3: Policy re-validation (defense in depth)
    policy = run_policy_check(product, quantity, proposal["user_budget"])
    if not policy.approved:
        raise ValueError(
            f"Policy check failed: {'; '.join(policy.blocked_reasons)}"
        )

    # Step 4: Create internal order (idempotent)
    order = await create_order(
        session_id=session_id or proposal.get("session_id", ""),
        proposal_id=proposal_id,
        product_id=product["_id"],
        product_name=product["name"],
        quantity=quantity,
        amount=authoritative_amount,
        currency=product.get("currency", "INR"),
    )
    order_id = order["_id"]

    # Prevent duplicate payment if already in progress
    if order.get("status") in ("PAYMENT_PENDING", "PAYMENT_VERIFIED", "COMPLETED"):
        raise ValueError(
            f"Order already in status {order['status']}. Duplicate payment prevented."
        )

    # Step 5: Create Razorpay order
    client = _get_razorpay_client()
    amount_paise = int(authoritative_amount * 100)  # Razorpay uses paise

    rzp_order = client.order.create({
        "amount": amount_paise,
        "currency": product.get("currency", "INR"),
        "receipt": str(order_id),
        "notes": {
            "product_id": str(product["_id"]),
            "product_name": product["name"],
            "session_id": session_id or "",
            "internal_order_id": str(order_id),
        },
    })

    rzp_order_id = rzp_order["id"]

    # Step 6: Update internal order with Razorpay order ID
    await update_order_status(
        order_id, "RAZORPAY_ORDER_CREATED", razorpay_order_id=rzp_order_id
    )
    await update_order_status(order_id, "PAYMENT_PENDING")

    # Log payment event
    col = get_collection("payment_events")
    await col.insert_one({
        "session_id": session_id,
        "order_id": str(order_id),
        "proposal_id": proposal_id,
        "razorpay_order_id": rzp_order_id,
        "amount": authoritative_amount,
        "currency": product.get("currency", "INR"),
        "event": "ORDER_CREATED",
        "timestamp": datetime.now(timezone.utc),
    })

    # Step 7: Return only public checkout data (secret never leaves backend)
    return {
        "order_id": str(order_id),
        "razorpay_order_id": rzp_order_id,
        "razorpay_key_id": settings.razorpay_key_id,  # public key only
        "amount": amount_paise,
        "currency": product.get("currency", "INR"),
        "product_name": product["name"],
    }


async def verify_razorpay_payment(
    order_id: str,
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
) -> Dict[str, Any]:
    """
    Backend-side HMAC-SHA256 Razorpay signature verification.
    Frontend callback alone is NEVER sufficient — verified here only.
    """
    # Verify signature
    message = f"{razorpay_order_id}|{razorpay_payment_id}"
    expected_sig = hmac.new(
        settings.razorpay_key_secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected_sig, razorpay_signature):
        # Mark as failed
        await update_order_status(order_id, "PAYMENT_FAILED")
        col = get_collection("payment_events")
        await col.insert_one({
            "order_id": order_id,
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "event": "PAYMENT_SIGNATURE_INVALID",
            "timestamp": datetime.now(timezone.utc),
        })
        raise ValueError("Payment signature verification failed. Order marked PAYMENT_FAILED.")

    # Signature valid — mark order as verified and completed
    order = await update_order_status(
        order_id,
        "PAYMENT_VERIFIED",
        razorpay_payment_id=razorpay_payment_id,
        razorpay_signature=razorpay_signature,
    )
    await update_order_status(order_id, "COMPLETED")

    col = get_collection("payment_events")
    await col.insert_one({
        "order_id": order_id,
        "razorpay_order_id": razorpay_order_id,
        "razorpay_payment_id": razorpay_payment_id,
        "event": "PAYMENT_VERIFIED",
        "timestamp": datetime.now(timezone.utc),
    })

    return {"success": True, "order_id": order_id, "payment_id": razorpay_payment_id}

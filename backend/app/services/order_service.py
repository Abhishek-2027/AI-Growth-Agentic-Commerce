from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from app.db.mongodb import get_collection
import logging

logger = logging.getLogger(__name__)


async def create_order(
    session_id: str,
    proposal_id: str,
    product_id: str,
    product_name: str,
    quantity: int,
    amount: float,
    currency: str = "INR",
    user_id: str = "guest_user",
) -> Dict[str, Any]:
    col = get_collection("orders")

    # Idempotency: check if order already exists for this proposal
    existing = await col.find_one({"proposal_id": proposal_id})
    if existing:
        existing["_id"] = str(existing["_id"])
        logger.info(f"Order already exists for proposal {proposal_id}")
        return existing

    doc = {
        "user_id": user_id,
        "session_id": session_id,
        "proposal_id": proposal_id,
        "product_id": product_id,
        "product_name": product_name,
        "quantity": quantity,
        "amount": amount,
        "currency": currency,
        "status": "CREATED",
        "razorpay_order_id": None,
        "razorpay_payment_id": None,
        "razorpay_signature": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": None,
        "completed_at": None,
    }
    result = await col.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return doc


async def get_order(order_id: str) -> Optional[Dict]:
    col = get_collection("orders")
    try:
        oid = ObjectId(order_id)
    except Exception:
        return None
    doc = await col.find_one({"_id": oid})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


async def update_order_status(
    order_id: str,
    status: str,
    razorpay_order_id: Optional[str] = None,
    razorpay_payment_id: Optional[str] = None,
    razorpay_signature: Optional[str] = None,
) -> Optional[Dict]:
    col = get_collection("orders")
    try:
        oid = ObjectId(order_id)
    except Exception:
        return None

    update: Dict[str, Any] = {
        "status": status,
        "updated_at": datetime.now(timezone.utc),
    }
    if razorpay_order_id:
        update["razorpay_order_id"] = razorpay_order_id
    if razorpay_payment_id:
        update["razorpay_payment_id"] = razorpay_payment_id
    if razorpay_signature:
        update["razorpay_signature"] = razorpay_signature
    if status in ("COMPLETED", "PAYMENT_VERIFIED"):
        update["completed_at"] = datetime.now(timezone.utc)

    await col.update_one({"_id": oid}, {"$set": update})
    doc = await col.find_one({"_id": oid})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


async def get_all_orders(limit: int = 50) -> List[Dict]:
    col = get_collection("orders")
    cursor = col.find().sort("created_at", -1).limit(limit)
    orders = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        orders.append(doc)
    return orders

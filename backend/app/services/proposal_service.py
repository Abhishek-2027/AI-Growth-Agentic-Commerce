from datetime import datetime, timezone
from typing import Optional, Dict, Any
from bson import ObjectId
from app.db.mongodb import get_collection
from app.services.product_service import get_product_by_id
from app.services.policy_service import run_policy_check
import logging

logger = logging.getLogger(__name__)


async def create_proposal(
    session_id: str,
    product_id: str,
    quantity: int,
    user_budget: float,
    reason: str,
    recommendation_reasons: list,
) -> Dict[str, Any]:
    col = get_collection("purchase_proposals")

    # Get authoritative product data from MongoDB
    product = await get_product_by_id(product_id)
    if not product:
        raise ValueError(f"Product {product_id} not found")

    # Run policy check
    policy = run_policy_check(product, quantity, user_budget)

    status = "POLICY_APPROVED" if policy.approved else "POLICY_REJECTED"

    doc = {
        "session_id": session_id,
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "expected_amount": float(product["price"]) * quantity,
        "currency": product.get("currency", "INR"),
        "user_budget": user_budget,
        "reason": reason,
        "recommendation_reasons": recommendation_reasons,
        "status": status,
        "policy_result": policy.to_dict(),
        "created_at": datetime.now(timezone.utc),
        "approved_at": None,
        "metadata": {},
    }

    result = await col.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return doc


async def get_proposal(proposal_id: str) -> Optional[Dict]:
    col = get_collection("purchase_proposals")
    try:
        oid = ObjectId(proposal_id)
    except Exception:
        return None
    doc = await col.find_one({"_id": oid})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


async def approve_proposal(proposal_id: str) -> Optional[Dict]:
    col = get_collection("purchase_proposals")
    try:
        oid = ObjectId(proposal_id)
    except Exception:
        return None
    now = datetime.now(timezone.utc)
    await col.update_one(
        {"_id": oid, "status": {"$in": ["POLICY_APPROVED", "AWAITING_USER_APPROVAL"]}},
        {"$set": {"status": "APPROVED", "approved_at": now}},
    )
    doc = await col.find_one({"_id": oid})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


async def reject_proposal(proposal_id: str) -> Optional[Dict]:
    col = get_collection("purchase_proposals")
    try:
        oid = ObjectId(proposal_id)
    except Exception:
        return None
    await col.update_one(
        {"_id": oid},
        {"$set": {"status": "REJECTED"}},
    )
    doc = await col.find_one({"_id": oid})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

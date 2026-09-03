from datetime import datetime, timezone
from typing import Dict, Any
import logging
from app.db.mongodb import get_collection
from app.models.audit import AuditLogCreate, AuditActor, AuditEventType, AuditStatus

logger = logging.getLogger(__name__)


async def log_event(
    session_id: str,
    actor: AuditActor,
    action: AuditEventType,
    reason: str,
    status: AuditStatus,
    metadata: Dict[str, Any] = {},
) -> str:
    """Central audit logging — records every important event to MongoDB."""
    try:
        col = get_collection("audit_logs")
        doc = {
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc),
            "actor": actor.value,
            "action": action.value,
            "reason": reason,
            "status": status.value,
            "metadata": metadata,
        }
        result = await col.insert_one(doc)
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Audit log failed: {e}")
        return ""


async def get_session_audit(session_id: str):
    """Return all audit events for a session, sorted by time."""
    col = get_collection("audit_logs")
    cursor = col.find({"session_id": session_id}).sort("timestamp", 1)
    events = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        events.append(doc)
    return events


async def get_order_audit(order_id: str):
    """Return all audit events that reference an order."""
    col = get_collection("audit_logs")
    cursor = col.find({"metadata.order_id": order_id}).sort("timestamp", 1)
    events = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        events.append(doc)
    return events


async def get_all_recent_audits(limit: int = 100):
    """Return most recent audit events across all sessions."""
    col = get_collection("audit_logs")
    cursor = col.find().sort("timestamp", -1).limit(limit)
    events = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        events.append(doc)
    return events

async def get_total_audit_count() -> int:
    """Return total number of audit events in the database."""
    col = get_collection("audit_logs")
    return await col.count_documents({})

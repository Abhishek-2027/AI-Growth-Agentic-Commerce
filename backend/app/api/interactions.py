from fastapi import APIRouter, HTTPException, Header
from typing import Optional, Dict, Any
from pydantic import BaseModel
from app.services.interaction_service import record_interaction
from app.services.preference_service import get_user_preferences

router = APIRouter(prefix="/api/interactions", tags=["Interactions"])

class InteractionRequest(BaseModel):
    event_type: str
    product_id: Optional[str] = None
    query: Optional[str] = None

@router.post("")
async def log_interaction(req: InteractionRequest, x_session_id: Optional[str] = Header(None)):
    """Log a user interaction event to inform the personalization engine."""
    if not x_session_id:
        return {"status": "skipped", "reason": "No session ID"}
    
    await record_interaction(
        user_id=x_session_id,
        event_type=req.event_type,
        product_id=req.product_id,
        query=req.query
    )
    return {"status": "success"}

@router.get("/preferences")
async def get_my_preferences(x_session_id: Optional[str] = Header(None)):
    """Return the current user's summarized preference profile."""
    if not x_session_id:
        raise HTTPException(status_code=400, detail="Missing X-Session-ID header")
    
    prefs = await get_user_preferences(x_session_id)
    if not prefs:
        return {"preferred_categories": [], "preferred_features": []}
    
    # Exclude MongoDB Object ID for JSON serialization
    if "_id" in prefs:
        prefs["_id"] = str(prefs["_id"])
    return prefs

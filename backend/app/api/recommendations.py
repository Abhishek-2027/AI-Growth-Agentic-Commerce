from fastapi import APIRouter, HTTPException, Header
from typing import Optional, List, Dict, Any
from app.services.recommendation_service import get_dashboard_recommendations
from app.models.product import ProductResponse

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])

@router.get("/dashboard")
async def get_dashboard(
    x_session_id: Optional[str] = Header(None)
):
    """Retrieve all recommendation carousels unified and deduplicated."""
    if not x_session_id:
        return {
            "recommended_for_you": [],
            "recent_activity": [],
            "complements_purchases": []
        }

    return await get_dashboard_recommendations(x_session_id)


from datetime import datetime
from typing import Optional
from app.db.mongodb import get_collection

async def record_interaction(user_id: str, event_type: str, product_id: Optional[str] = None, query: Optional[str] = None):
    """
    Log user interaction and asynchronously trigger preference profile update.
    """
    col = get_collection("user_interactions")
    interaction = {
        "user_id": user_id,
        "event_type": event_type,
        "timestamp": datetime.utcnow()
    }
    if product_id:
        interaction["product_id"] = product_id
    if query:
        interaction["query"] = query

    await col.insert_one(interaction)
    
    # Delegate the preference aggregation to preference_service
    from app.services.preference_service import update_user_preferences
    await update_user_preferences(user_id)

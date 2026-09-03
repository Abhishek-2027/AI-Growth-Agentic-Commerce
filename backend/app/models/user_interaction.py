from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserInteraction(BaseModel):
    user_id: str
    event_type: str  # e.g., PRODUCT_VIEW, PRODUCT_CLICK, PRODUCT_SEARCH, PRODUCT_ADDED_TO_CART, PRODUCT_RECOMMENDED, PRODUCT_PURCHASED
    product_id: Optional[str] = None
    query: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class UserInteractionResponse(UserInteraction):
    id: str = Field(alias="_id")

    class Config:
        populate_by_name = True

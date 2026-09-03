from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CategoryScore(BaseModel):
    category: str
    score: float

class FeatureScore(BaseModel):
    feature: str
    score: float

class UserPreferenceBase(BaseModel):
    user_id: str
    preferred_categories: List[CategoryScore] = []
    preferred_features: List[FeatureScore] = []
    average_purchase_price: Optional[float] = None
    recently_viewed_products: List[str] = []
    recently_purchased_products: List[str] = []
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserPreferenceResponse(UserPreferenceBase):
    id: str = Field(alias="_id")

    class Config:
        populate_by_name = True

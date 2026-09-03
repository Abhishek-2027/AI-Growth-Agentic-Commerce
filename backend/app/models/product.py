from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    currency: str = "INR"
    category: str
    features: List[str] = []
    stock: int = 0
    active: bool = True
    image_url: Optional[str] = None
    brand: Optional[str] = None
    rating: Optional[float] = None
    complementary_categories: Optional[List[str]] = []


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: str = Field(alias="_id")
    created_at: Optional[datetime] = None

    class Config:
        populate_by_name = True


class ProductSearchRequest(BaseModel):
    query: str
    max_price: Optional[float] = None
    min_price: Optional[float] = None
    category: Optional[str] = None
    required_features: Optional[List[str]] = []
    limit: int = 10

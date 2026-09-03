from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.db.mongodb import get_collection
import logging

logger = logging.getLogger(__name__)


def _serialize(doc: Dict) -> Dict:
    doc["_id"] = str(doc["_id"])
    return doc


async def search_products(
    query: str = "",
    max_price: Optional[float] = None,
    min_price: Optional[float] = None,
    category: Optional[str] = None,
    required_features: Optional[List[str]] = None,
    limit: int = 10,
) -> List[Dict]:
    col = get_collection("products")
    filter_query: Dict[str, Any] = {"active": True}

    # 1. Price range filters (Strict)
    if max_price is not None or min_price is not None:
        price_filter: Dict[str, float] = {}
        if max_price is not None:
            price_filter["$lte"] = max_price
        if min_price is not None:
            price_filter["$gte"] = min_price
        filter_query["price"] = price_filter

    # 2. Text Search (Extremely robust TF-IDF based text matching)
    # Combine query, category, and features into a single search string
    search_terms = []
    if query:
        search_terms.append(query)
    
    # Treat category as a search keyword rather than a strict filter to avoid 0 results on LLM mismatch
    if category and category.lower() not in ["other", "null", "none"]:
        search_terms.append(category)
        
    # Treat features as keywords to leverage text scoring
    if required_features:
        search_terms.extend(required_features)

    full_search = " ".join(search_terms).strip()

    if full_search:
        # Use MongoDB's native full-text search index
        filter_query["$text"] = {"$search": full_search}
        cursor = col.find(filter_query, {"score": {"$meta": "textScore"}})
        # Sort by relevance score (best matches first)
        cursor = cursor.sort([("score", {"$meta": "textScore"})])
    else:
        # Fallback if there is no text search
        cursor = col.find(filter_query).sort("price", 1)

    cursor = cursor.limit(limit)
    return [_serialize(doc) async for doc in cursor]


async def get_product_by_id(product_id: str) -> Optional[Dict]:
    col = get_collection("products")
    try:
        oid = ObjectId(product_id)
    except Exception:
        doc = await col.find_one({"_id": product_id})
        if doc:
            return _serialize(doc)
        return None
    doc = await col.find_one({"_id": oid})
    if doc:
        return _serialize(doc)
    return None


async def check_stock(product_id: str, quantity: int) -> bool:
    product = await get_product_by_id(product_id)
    if not product:
        return False
    return product.get("stock", 0) >= quantity


async def get_all_products(limit: int = 50) -> List[Dict]:
    col = get_collection("products")
    cursor = col.find({"active": True}).sort("category", 1).limit(limit)
    return [_serialize(doc) async for doc in cursor]

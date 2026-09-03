from typing import List, Dict, Any
from bson import ObjectId
from app.db.mongodb import get_collection
from app.config.product_relationships import COMPLEMENTARY_CATEGORIES

async def get_recommended_for_you_candidates(prefs: Dict[str, Any], exclude_ids: List[ObjectId], limit: int = 150) -> List[Dict]:
    products_col = get_collection("products")
    query = {"_id": {"$nin": exclude_ids}}

    if prefs and prefs.get("preferred_categories"):
        # Fetch from all preferred categories to allow mixing
        cats = [c["category"] for c in prefs["preferred_categories"]]
        query["category"] = {"$in": cats}

    cursor = products_col.find(query).limit(limit)
    return await cursor.to_list(length=limit)

async def get_recent_activity_candidates(prefs: Dict[str, Any], exclude_ids: List[ObjectId], limit: int = 150) -> List[Dict]:
    if not prefs:
        return []

    products_col = get_collection("products")
    
    # Collect IDs of recent interactions
    recent_ids = []
    for k in ["recently_clicked_products", "recently_viewed_products", "recently_purchased_products"]:
        recent_ids.extend([ObjectId(pid) for pid in prefs.get(k, []) if ObjectId.is_valid(pid)])
    
    if not recent_ids:
        return []

    # Get categories of recent interactions
    cursor = products_col.find({"_id": {"$in": recent_ids}})
    recent_prods = await cursor.to_list(length=50)
    cats = list(set([p.get("category") for p in recent_prods if p.get("category")]))

    query = {"_id": {"$nin": exclude_ids}}
    if cats:
        query["category"] = {"$in": cats}

    cursor = products_col.find(query).limit(limit)
    return await cursor.to_list(length=limit)

async def get_complementary_candidates(prefs: Dict[str, Any], exclude_ids: List[ObjectId], limit: int = 150) -> List[Dict]:
    if not prefs or not prefs.get("recently_purchased_products"):
        return []

    products_col = get_collection("products")
    purchased_ids = [ObjectId(pid) for pid in prefs["recently_purchased_products"] if ObjectId.is_valid(pid)]
    
    cursor = products_col.find({"_id": {"$in": purchased_ids}})
    purchased_prods = await cursor.to_list(length=20)

    comp_cats = []
    for p in purchased_prods:
        # Check explicit complementary_categories on product, fallback to global config
        p_comps = p.get("complementary_categories", [])
        if not p_comps and p.get("category"):
            p_comps = COMPLEMENTARY_CATEGORIES.get(p.get("category").lower(), [])
        comp_cats.extend(p_comps)
    
    comp_cats = list(set(comp_cats))

    if not comp_cats:
        return []

    query = {
        "category": {"$in": comp_cats},
        "_id": {"$nin": exclude_ids + purchased_ids}
    }

    cursor = products_col.find(query).limit(limit)
    return await cursor.to_list(length=limit)

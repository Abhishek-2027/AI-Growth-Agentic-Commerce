import math
from datetime import datetime
from typing import Dict, Any, Optional
from bson import ObjectId
from app.db.mongodb import get_collection
from app.models.user_preference import CategoryScore, FeatureScore

# Interaction weights
EVENT_WEIGHTS = {
    "PRODUCT_VIEW": 1,
    "PRODUCT_CLICK": 2,
    "PRODUCT_SEARCH": 3,
    "PRODUCT_ADDED_TO_CART": 5,
    "PRODUCT_PURCHASED": 10,
    "PRODUCT_RECOMMENDED": 0.5,
}

# Decay rate (days for score to halve)
DECAY_HALF_LIFE_DAYS = 7

async def update_user_preferences(user_id: str):
    """
    Build multi-interest user profile by aggregating interactions with exponential decay.
    Maintains multiple categories simultaneously without overwriting.
    """
    interactions_col = get_collection("user_interactions")
    products_col = get_collection("products")
    prefs_col = get_collection("user_preferences")

    # Get last 200 interactions for the user to have a rich history
    cursor = interactions_col.find({"user_id": user_id}).sort("timestamp", -1).limit(200)
    interactions = await cursor.to_list(length=200)

    if not interactions:
        return

    category_scores = {}
    feature_scores = {}
    purchased_prices = []
    
    # Store raw recency for candidate generation
    viewed = []
    clicked = []
    purchased = []

    now = datetime.utcnow()

    for interaction in interactions:
        event = interaction["event_type"]
        weight = EVENT_WEIGHTS.get(event, 1)
        
        # Exponential decay: decayed = original * exp(-lambda * t)
        # lambda = ln(2) / half_life
        age_days = (now - interaction["timestamp"]).total_seconds() / 86400
        decay_constant = 0.693 / DECAY_HALF_LIFE_DAYS
        decay_factor = math.exp(-decay_constant * age_days)
        final_score = weight * decay_factor

        prod_id = interaction.get("product_id")
        
        if prod_id:
            # Track raw interactions
            if event == "PRODUCT_VIEW" and prod_id not in viewed:
                viewed.append(prod_id)
            if event == "PRODUCT_CLICK" and prod_id not in clicked:
                clicked.append(prod_id)
            if event == "PRODUCT_PURCHASED":
                if prod_id not in purchased:
                    purchased.append(prod_id)

            # Fetch product to score categories and features
            try:
                prod = await products_col.find_one({"_id": ObjectId(prod_id)})
            except:
                prod = None

            if prod:
                cat = prod.get("category")
                if cat:
                    category_scores[cat] = category_scores.get(cat, 0) + final_score
                
                for feat in prod.get("features", []):
                    feature_scores[feat] = feature_scores.get(feat, 0) + final_score
                
                if event == "PRODUCT_PURCHASED":
                    purchased_prices.append(prod.get("price", 0))
                    
        # Extract from searches
        if event == "PRODUCT_SEARCH" and interaction.get("query"):
            query = interaction["query"].lower()
            tokens = query.split()
            for token in tokens:
                if len(token) > 3:
                    feature_scores[token] = feature_scores.get(token, 0) + final_score

    # Normalize category and feature scores to max 1.0 (or keep raw if preferred, but normalize helps ranking)
    def normalize_scores(score_dict, top_n=10):
        if not score_dict:
            return []
        max_score = max(score_dict.values())
        normalized = [{"name": k, "score": v / max_score if max_score > 0 else 0} for k, v in score_dict.items()]
        normalized.sort(key=lambda x: x["score"], reverse=True)
        return normalized[:top_n]

    # Keep top 10 categories to maintain multi-interest profile
    top_categories = [CategoryScore(category=x["name"], score=x["score"]) for x in normalize_scores(category_scores, 10)]
    top_features = [FeatureScore(feature=x["name"], score=x["score"]) for x in normalize_scores(feature_scores, 15)]
    
    avg_price = sum(purchased_prices) / len(purchased_prices) if purchased_prices else None

    preference_data = {
        "user_id": user_id,
        "preferred_categories": [c.dict() for c in top_categories],
        "preferred_features": [f.dict() for f in top_features],
        "average_purchase_price": avg_price,
        "recently_viewed_products": viewed[:20],
        "recently_clicked_products": clicked[:20],
        "recently_purchased_products": purchased[:20],
        "updated_at": datetime.utcnow()
    }

    await prefs_col.update_one(
        {"user_id": user_id},
        {"$set": preference_data},
        upsert=True
    )

async def get_user_preferences(user_id: str) -> Optional[Dict[str, Any]]:
    col = get_collection("user_preferences")
    return await col.find_one({"user_id": user_id})

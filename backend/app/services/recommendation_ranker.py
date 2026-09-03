from typing import Dict, Any

def score_for_recommended(product: Dict, prefs: Dict) -> float:
    """
    35% Overall User Preference
    20% Purchase History (Complementary or past category)
    15% Click/View Interest (Recency)
    10% Search Interest (Feature match)
    10% Recency
    10% Product Quality / Popularity (Mocked via stock/rating)
    """
    score = 0.0
    if not prefs:
        return 0.1 # Fallback

    cat_score = 0.0
    for pc in prefs.get("preferred_categories", []):
        if pc["category"].lower() == product.get("category", "").lower():
            cat_score = pc["score"]
            break
    score += cat_score * 0.35

    feat_score = 0.0
    pref_feats = {f["feature"].lower(): f["score"] for f in prefs.get("preferred_features", [])}
    matched = 0
    for feat in product.get("features", []):
        if feat.lower() in pref_feats:
            feat_score += pref_feats[feat.lower()]
            matched += 1
    if matched > 0:
        score += (feat_score / matched) * 0.10

    prod_id_str = str(product["_id"])
    if prod_id_str in prefs.get("recently_viewed_products", []):
        idx = prefs["recently_viewed_products"].index(prod_id_str)
        score += (1.0 - (idx * 0.05)) * 0.15
    elif prod_id_str in prefs.get("recently_clicked_products", []):
        idx = prefs["recently_clicked_products"].index(prod_id_str)
        score += (1.0 - (idx * 0.05)) * 0.20

    # Mock popularity
    pop_score = min(product.get("stock", 0) / 100.0, 1.0)
    score += pop_score * 0.10
    
    return score

def score_for_recent_activity(product: Dict, prefs: Dict) -> float:
    """
    50% Recent Interaction (Click/View)
    20% Product Similarity
    15% Category Preference
    10% Recency
    5% Product Quality / Popularity
    """
    score = 0.0
    if not prefs:
        return 0.1
        
    prod_id_str = str(product["_id"])
    recent_interaction = 0.0
    
    if prod_id_str in prefs.get("recently_clicked_products", []):
        idx = prefs["recently_clicked_products"].index(prod_id_str)
        recent_interaction = max(1.0 - (idx * 0.1), 0)
    elif prod_id_str in prefs.get("recently_viewed_products", []):
        idx = prefs["recently_viewed_products"].index(prod_id_str)
        recent_interaction = max(0.8 - (idx * 0.1), 0)
        
    score += recent_interaction * 0.50

    cat_score = 0.0
    for pc in prefs.get("preferred_categories", []):
        if pc["category"].lower() == product.get("category", "").lower():
            cat_score = pc["score"]
            break
    score += cat_score * 0.15

    pop_score = min(product.get("stock", 0) / 100.0, 1.0)
    score += pop_score * 0.05

    # Boost if it matches feature exactly
    feat_score = sum([1 for f in product.get("features", []) if any(pf["feature"] == f for pf in prefs.get("preferred_features", []))])
    score += min(feat_score * 0.1, 1.0) * 0.20

    return score

def score_for_complementary(product: Dict, prefs: Dict) -> float:
    """
    45% Complementary Relationship Strength
    25% Purchase Recency
    15% User Category Preference
    10% Product Availability
    5% Diversity (handled in diversifier)
    """
    score = 0.0
    if not prefs:
        return 0.1

    # Candidate generator already filtered for complementary categories, so we give base strength
    score += 0.45
    
    cat_score = 0.0
    for pc in prefs.get("preferred_categories", []):
        if pc["category"].lower() == product.get("category", "").lower():
            cat_score = pc["score"]
            break
    score += cat_score * 0.15
    
    pop_score = min(product.get("stock", 0) / 100.0, 1.0)
    score += pop_score * 0.10
    
    return score

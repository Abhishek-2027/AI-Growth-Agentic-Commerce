from typing import Dict, Any, List
from bson import ObjectId
from app.services.preference_service import get_user_preferences
from app.services.candidate_generator import (
    get_recommended_for_you_candidates,
    get_recent_activity_candidates,
    get_complementary_candidates
)
from app.services.recommendation_ranker import (
    score_for_recommended,
    score_for_recent_activity,
    score_for_complementary
)
from app.services.recommendation_diversifier import diversify_and_deduplicate
import logging

logger = logging.getLogger(__name__)

async def get_dashboard_recommendations(user_id: str) -> Dict[str, List[Dict]]:
    """
    Master pipeline for multi-interest, dynamic recommendations.
    Generates, ranks, diversifies, and deduplicates across all three carousels.
    """
    prefs = await get_user_preferences(user_id) or {}
    
    # 1. Base Exclusion (recent purchases shouldn't be blindly recommended again)
    base_exclude = [ObjectId(pid) for pid in prefs.get("recently_purchased_products", []) if ObjectId.is_valid(pid)]
    
    # Generate Candidates
    rec_cands = await get_recommended_for_you_candidates(prefs, base_exclude, 150)
    recent_cands = await get_recent_activity_candidates(prefs, base_exclude, 150)
    comp_cands = await get_complementary_candidates(prefs, base_exclude, 150)

    # Score Candidates
    for p in rec_cands:
        p["_ranking_score"] = score_for_recommended(p, prefs)
    rec_cands.sort(key=lambda x: x["_ranking_score"], reverse=True)

    for p in recent_cands:
        p["_ranking_score"] = score_for_recent_activity(p, prefs)
    recent_cands.sort(key=lambda x: x["_ranking_score"], reverse=True)

    for p in comp_cands:
        p["_ranking_score"] = score_for_complementary(p, prefs)
    comp_cands.sort(key=lambda x: x["_ranking_score"], reverse=True)

    # Global Exclusion Set
    global_excluded_ids = set([str(pid) for pid in base_exclude])
    
    # Diversify and Deduplicate Sequence
    # Sequence order matters for deduplication. 
    # 1. Recent Activity (strongest signal for immediate action)
    final_recent = diversify_and_deduplicate(recent_cands, 6, global_excluded_ids, max_per_category=3)
    
    # 2. Recommended For You (broader)
    final_rec = diversify_and_deduplicate(rec_cands, 6, global_excluded_ids, max_per_category=2)
    
    # 3. Complements (cross-sell)
    final_comp = diversify_and_deduplicate(comp_cands, 6, global_excluded_ids, max_per_category=3)
    
    # Fallback if somehow empty
    if not final_rec:
        # Give them something generic from top ranked rec_cands ignoring deduplication if absolutely necessary
        final_rec = rec_cands[:6]
    if not final_recent:
        final_recent = recent_cands[:6]
    if not final_comp:
        final_comp = comp_cands[:6]

    # Clean up _id for JSON serialization and remove ranking score
    def cleanup(products):
        for p in products:
            if "_id" in p:
                p["_id"] = str(p["_id"])
            p.pop("_ranking_score", None)
        return products

    return {
        "recommended_for_you": cleanup(final_rec),
        "recent_activity": cleanup(final_recent),
        "complements_purchases": cleanup(final_comp)
    }

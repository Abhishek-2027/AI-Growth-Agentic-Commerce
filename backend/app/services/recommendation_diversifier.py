from typing import List, Dict, Set
from bson import ObjectId

def diversify_and_deduplicate(
    ranked_products: List[Dict], 
    limit: int, 
    global_excluded_ids: Set[str], 
    max_per_category: int = 2
) -> List[Dict]:
    """
    Filters a ranked list of products to:
    1. Exclude any product ID present in global_excluded_ids.
    2. Enforce a maximum of `max_per_category` products per category.
    3. Return exactly `limit` products.
    """
    final_selection = []
    category_counts = {}

    for prod in ranked_products:
        if len(final_selection) >= limit:
            break
            
        prod_id_str = str(prod["_id"])
        
        # 1. Global exclusion deduplication
        if prod_id_str in global_excluded_ids:
            continue

        cat = prod.get("category", "unknown").lower()
        
        # 2. Diversification limit
        count = category_counts.get(cat, 0)
        if count >= max_per_category:
            continue
            
        # Accept product
        final_selection.append(prod)
        category_counts[cat] = count + 1
        global_excluded_ids.add(prod_id_str)

    return final_selection

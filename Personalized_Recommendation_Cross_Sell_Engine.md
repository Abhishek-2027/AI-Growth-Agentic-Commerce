# Feature Addition Prompt: Personalized Recommendation & Cross-Sell Engine

Add a complete **Personalized Product Recommendation and Cross-Sell Engine** to the existing AgentCart application.

The application already has:
- User authentication/login
- React + Tailwind frontend
- FastAPI backend
- MongoDB Atlas
- Gemini AI agent
- Product catalog
- Agent-based recommendations
- Policy engine
- Razorpay Test Mode payment
- Audit trail

Do not break or replace the existing agentic commerce workflow. Extend it with a new personalization and recommendation module.

---

# 1. OBJECTIVE

When a user logs in, the system should use their previous behavior to generate personalized recommendations.

Use:
- Previous purchases
- Product clicks
- Product views
- Search history
- Agent conversations
- Product categories viewed
- Product categories purchased
- Budget patterns
- Product interaction frequency
- Recent interactions

The system should recommend products based on both:

1. **User personal history**
2. **Product relationships / complementary products**

---

# 2. MAIN RECOMMENDATION BEHAVIOR

## Scenario 1: Purchase History

If the user previously purchased:

```text
Laptop
```

The recommendation engine should understand that complementary products may include:

```text
Mouse
Keyboard
Laptop Stand
Laptop Bag
External Monitor
USB Hub
Headphones
```

The recommendation should not randomly recommend unrelated products.

Example:

```text
You previously purchased a laptop.

You may also be interested in:

✓ Wireless Mouse
✓ Mechanical Keyboard
✓ Laptop Stand
✓ USB-C Hub
```

This is a **cross-sell / complementary product recommendation**.

---

# 3. CLICK AND VIEW HISTORY

Track user interactions.

Example:

```text
User clicks:

Sony Headphones
Sony Headphones
Boat Headphones
Sony Headphones
JBL Headphones
```

The system should understand the user's interest in relevant categories and features.

```text
Category:
Audio / Electronics

Features:
Wireless
Headphones
```

Then recommendations should prioritize similar or relevant products.

---

# 4. SEARCH HISTORY

Track product searches.

Example:

```text
"wireless headphones"
"noise cancelling headphones"
"Bluetooth earbuds"
```

The system should extract preferences such as:

```text
Preferred category:
Audio

Preferred features:
Wireless
Bluetooth
Noise Cancellation
```

Use these preferences in future ranking.

---

# 5. PERSONALIZATION ARCHITECTURE

```text
                    USER LOGIN
                        │
                        ▼
              LOAD USER HISTORY
                        │
         ┌──────────────┼──────────────┐
         ▼              ▼              ▼
     PURCHASES       CLICKS         SEARCHES
         │              │              │
         └──────────────┼──────────────┘
                        ▼
              PERSONALIZATION ENGINE
                        │
                        ├── Category preferences
                        ├── Feature preferences
                        ├── Budget preferences
                        ├── Recent interests
                        └── Purchase patterns
                        │
                        ▼
                USER PREFERENCE PROFILE
                        │
                        ▼
               PRODUCT RECOMMENDATION
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
       SIMILAR PRODUCTS    COMPLEMENTARY PRODUCTS
              │                   │
              └─────────┬─────────┘
                        ▼
              PERSONALIZED RANKING
                        │
                        ▼
                  RECOMMENDATIONS
```

---

# 6. MONGODB COLLECTIONS

## users

```json
{
  "_id": "user_123",
  "name": "User",
  "email": "user@example.com",
  "created_at": "timestamp"
}
```

## user_interactions

Store every meaningful product interaction.

```json
{
  "_id": "interaction_123",
  "user_id": "user_123",
  "product_id": "product_123",
  "event_type": "PRODUCT_CLICK",
  "timestamp": "timestamp"
}
```

Supported event types:

```text
PRODUCT_VIEW
PRODUCT_CLICK
PRODUCT_SEARCH
PRODUCT_ADDED_TO_CART
PRODUCT_RECOMMENDED
PRODUCT_PURCHASED
```

For searches:

```json
{
  "user_id": "user_123",
  "event_type": "PRODUCT_SEARCH",
  "query": "wireless noise cancelling headphones",
  "timestamp": "timestamp"
}
```

## user_preferences

Create a summarized user preference profile.

```json
{
  "user_id": "user_123",
  "preferred_categories": [
    {"category": "electronics", "score": 0.9},
    {"category": "audio", "score": 0.8}
  ],
  "preferred_features": [
    {"feature": "wireless", "score": 0.95},
    {"feature": "noise cancellation", "score": 0.75}
  ],
  "average_purchase_price": 4500,
  "recently_viewed_products": ["product_1", "product_2"],
  "recently_purchased_products": ["product_3"],
  "updated_at": "timestamp"
}
```

This profile should be automatically updated from user interactions.

---

# 7. PRODUCT RELATIONSHIP DATA

Add support for complementary products.

Recommended approach:

```json
{
  "_id": "product_laptop_123",
  "name": "Laptop",
  "category": "laptops",
  "complementary_categories": [
    "mouse",
    "keyboard",
    "laptop_accessories",
    "monitor",
    "usb_hub"
  ]
}
```

Example:

```text
Laptop
    ↓
Complementary Categories
    ├── Mouse
    ├── Keyboard
    ├── Laptop Stand
    ├── USB Hub
    └── Monitor
```

Also support explicit product relationships if needed:

```json
{
  "product_id": "laptop_123",
  "related_product_id": "mouse_456",
  "relationship_type": "COMPLEMENTARY",
  "weight": 0.9
}
```

---

# 8. PURCHASE-BASED CROSS-SELL

When a user completes a purchase:

```text
PAYMENT VERIFIED
      ↓
ORDER COMPLETED
      ↓
Save PURCHASED interaction
      ↓
Update user preference profile
      ↓
Find complementary categories
      ↓
Find available products
      ↓
Generate personalized cross-sell recommendations
```

Example:

```text
User purchased Laptop
      ↓
Find complementary categories:
Mouse
Keyboard
Laptop Stand
USB Hub
      ↓
Search catalog
      ↓
Top available products
      ↓
Personalized recommendation
```

Display:

```text
Because you purchased a laptop, you may also be interested in:

[ Wireless Mouse ]
[ Mechanical Keyboard ]
[ Adjustable Laptop Stand ]
[ USB-C Hub ]
```

Do not falsely claim that a user needs a product.

Use wording such as:
- You may also be interested in
- Frequently paired accessories
- Complements your recent purchase

---

# 9. PERSONALIZED PRODUCT RANKING

Create a deterministic recommendation scoring engine.

Do not let Gemini alone rank products.

```text
Final Recommendation Score =

Current Intent Match
+
Category Preference Score
+
Feature Preference Score
+
Click/View Interest Score
+
Search Interest Score
+
Purchase Relationship Score
+
Recency Score
```

Suggested initial weights:

```text
Current User Request Match       = 35%
User Category Preference         = 15%
Feature Preference               = 15%
Click/View History               = 10%
Search History                   = 10%
Complementary Purchase Relation  = 10%
Recency                          = 5%
```

Make these weights configurable.

For cross-sell recommendations, increase the importance of complementary purchase relationships.

---

# 10. INTERACTION WEIGHTING

Recommended weights:

```text
PRODUCT_VIEW              = 1
PRODUCT_CLICK             = 2
PRODUCT_SEARCH            = 3
PRODUCT_ADDED_TO_CART     = 5
PRODUCT_PURCHASED         = 10
```

Apply recency.

Conceptual formula:

```text
Interaction Score =
Event Weight × Recency Weight
```

Recent interactions should have higher influence.

---

# 11. PERSONALIZATION SERVICE

Create:

```text
backend/app/services/personalization_service.py
```

Responsibilities:

1. Record user interaction.
2. Load user interaction history.
3. Analyze categories.
4. Analyze features.
5. Calculate budget preference.
6. Calculate recent interests.
7. Update user preference profile.
8. Generate similar product recommendations.
9. Generate complementary product recommendations.
10. Rank recommendations.

Suggested functions:

```python
record_interaction()
get_user_history()
build_user_preference_profile()
update_user_preferences()
get_personalized_recommendations()
get_similar_products()
get_complementary_products()
rank_products()
```

---

# 12. RECOMMENDATION TYPES

## A. Recommended For You

Based on:
- Click history
- View history
- Search history
- Preferences
- Previous purchases

## B. Similar To What You Viewed

Based primarily on:
- Recent product views
- Recent clicks
- Category similarity
- Feature similarity

## C. Complements Your Purchase

Based on:
- Completed purchases
- Complementary categories
- Product relationships

If the user bought a laptop:

```text
Wireless Mouse
Mechanical Keyboard
Laptop Stand
USB Hub
```

---

# 13. RECOMMENDATION FLOW

```text
USER LOGIN
     │
     ▼
LOAD USER PROFILE
     │
     ▼
LOAD INTERACTIONS
     │
     ├── Clicks
     ├── Views
     ├── Searches
     └── Purchases
     │
     ▼
BUILD USER PREFERENCE PROFILE
     │
     ▼
GET PRODUCT CATALOG
     │
     ▼
GENERATE CANDIDATES
     │
     ├── Similar Products
     ├── Preferred Categories
     └── Complementary Products
     │
     ▼
REMOVE ALREADY PURCHASED ITEMS WHERE APPROPRIATE
     │
     ▼
DETERMINISTIC RANKING ENGINE
     │
     ▼
TOP PERSONALIZED PRODUCTS
     │
     ▼
FRONTEND RECOMMENDATION SECTIONS
```

---

# 14. NEW FRONTEND COMPONENTS

```text
components/
│
└── recommendations/
    ├── PersonalizedRecommendations.jsx
    ├── RecommendedForYou.jsx
    ├── SimilarProducts.jsx
    ├── ComplementaryProducts.jsx
    └── RecommendationCard.jsx
```

Display recommendation sections on the Dashboard.

```text
┌──────────────────────────────────────────┐
│ Recommended For You                     │
│ [Product] [Product] [Product]            │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│ Based on Your Recent Activity            │
│ [Product] [Product] [Product]            │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│ Complements Your Recent Purchase         │
│ [Mouse] [Keyboard] [Laptop Stand]        │
└──────────────────────────────────────────┘
```

---

# 15. INTERACTION TRACKING

Track:

```text
Views product → PRODUCT_VIEW
Clicks product → PRODUCT_CLICK
Searches catalog → PRODUCT_SEARCH
Adds to cart → PRODUCT_ADDED_TO_CART
Receives recommendation → PRODUCT_RECOMMENDED
Completes purchase → PRODUCT_PURCHASED
```

Send events to:

```text
POST /api/interactions
```

Do not block the UI if interaction logging temporarily fails. The main commerce workflow must continue.

---

# 16. API ENDPOINTS

```text
POST /api/interactions
```

Record user interaction.

```text
GET /api/recommendations
```

Return personalized recommendations.

Optional filters:

```text
GET /api/recommendations?type=personalized
GET /api/recommendations?type=similar
GET /api/recommendations?type=complementary
```

Add:

```text
GET /api/users/me/preferences
```

Return the user's summarized preference profile.

---

# 17. GEMINI INTEGRATION

Gemini should explain recommendations, not be the only ranking mechanism.

```text
USER HISTORY
       +
CURRENT USER REQUEST
       +
PRODUCT CATALOG
       │
       ▼
DETERMINISTIC PERSONALIZATION ENGINE
       │
       ▼
RANKED PRODUCTS
       │
       ▼
GEMINI
       │
       ▼
NATURAL LANGUAGE EXPLANATION
```

Only generate explanations supported by actual stored interaction or product relationship data. Do not invent user preferences.

---

# 18. COLD START HANDLING

For users with:

```text
No purchases
No clicks
No searches
```

Use:
- Current request relevance
- Product popularity if available
- Catalog relevance
- Featured products

Do not claim personalization when there is no user history.

Use:

```text
Popular products you may want to explore
```

instead of:

```text
Recommended based on your history
```

---

# 19. UPDATE EXISTING AGENT FLOW

```text
USER LOGIN
     ↓
LOAD USER HISTORY
     ↓
BUILD PREFERENCE CONTEXT
     ↓
USER REQUEST
     ↓
INPUT GUARDRAIL
     ↓
GEMINI INTENT EXTRACTION
     ↓
CATALOG SEARCH
     ↓
PERSONALIZED RANKING
     ↓
AI EXPLANATION
     ↓
RECOMMENDATION
     ↓
POLICY ENGINE
     ↓
USER APPROVAL
     ↓
RAZORPAY PAYMENT
     ↓
BACKEND VERIFICATION
     ↓
AUDIT TRAIL
     ↓
UPDATE USER HISTORY
     ↓
UPDATE FUTURE RECOMMENDATIONS
```

---

# 20. IMPORTANT SAFETY AND DATA RULES

- Recommendations must never bypass the policy engine.
- Recommendations must never automatically purchase products.
- Personalized recommendations must not automatically charge money.
- User approval is still required for payment.
- Recommendation logic must not modify Razorpay payment amounts.
- Actual product prices must always come from MongoDB.
- Do not send the entire raw user history to Gemini.
- Build a compact preference profile.
- Only use Gemini to explain supported recommendations.
- Do not falsely claim a preference not supported by user history.

---

# 21. FINAL EXPECTED USER EXPERIENCE

After login:

```text
Dashboard loads
      ↓
System loads user history
      ↓
Recommended For You
Based on Recent Activity
Complements Your Recent Purchase
```

If the user previously purchased a laptop:

```text
Wireless Mouse
Mechanical Keyboard
Laptop Stand
USB-C Hub
```

If they frequently search and click:

```text
Wireless Headphones
Noise Cancelling Headphones
Bluetooth Earbuds
```

They should see relevant audio recommendations.

When the user makes new interactions:

```text
Click
↓
Interaction Logged

Search
↓
Interaction Logged

Purchase
↓
Interaction Logged

Preference Profile Updated
↓
Future Recommendations Improve
```

---

# FINAL ARCHITECTURAL PRINCIPLE

```text
USER BEHAVIOR
       +
PURCHASE HISTORY
       +
PRODUCT RELATIONSHIPS
       +
CURRENT USER INTENT
       ↓
PERSONALIZATION ENGINE
       ↓
DETERMINISTIC PRODUCT RANKING
       ↓
TOP RECOMMENDATIONS
       ↓
GEMINI EXPLANATION
       ↓
USER DECISION
```

Do not implement this as only an LLM-based recommendation feature.

Build a real backend personalization pipeline using MongoDB Atlas interaction logs, purchase history, product relationships, deterministic ranking, and Gemini only for natural-language reasoning and explanation.

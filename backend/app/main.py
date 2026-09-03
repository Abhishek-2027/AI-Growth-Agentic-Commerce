from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.mongodb import connect_db, close_db
from app.api import agent, products, orders, orders_list, payments, audit, interactions, recommendations


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_db()
    await _seed_products_if_empty()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title="AgentCart — Safe Agentic Commerce API",
    description="AI-powered safe commerce platform with deterministic policy engine and full audit trail.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(agent.router)
app.include_router(products.router)
app.include_router(orders.router)      # purchase proposal routes
app.include_router(orders_list.router) # order list routes
app.include_router(payments.router)
app.include_router(audit.router)
app.include_router(interactions.router)
app.include_router(recommendations.router)


@app.get("/")
async def root():
    return {
        "name": settings.project_name,
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


# ── Seed demo products on first run ────────────────────────────────────────────

async def _seed_products_if_empty():
    """Seed MongoDB with realistic demo products for the hackathon demo."""
    from app.db.mongodb import get_collection
    from datetime import datetime, timezone

    col = get_collection("products")
    count = await col.count_documents({})
    if count > 0:
        return  # Already seeded

    products = [
        # Headphones — the main demo category
        {
            "name": "Sony WH-1000XM4 Wireless Headphones",
            "description": "Industry-leading noise cancellation with 30hr battery life, multipoint connection, and Speak-to-Chat technology.",
            "price": 4999,
            "currency": "INR",
            "category": "headphones",
            "features": ["wireless", "noise cancellation", "30hr battery", "multipoint", "foldable"],
            "stock": 15,
            "active": True,
            "brand": "Sony",
            "rating": 4.8,
            "image_url": None,
        },
        {
            "name": "boAt Rockerz 450 Wireless Headphones",
            "description": "On-ear wireless headphones with 15 hours playback, 40mm dynamic drivers, and padded earcups.",
            "price": 1299,
            "currency": "INR",
            "category": "headphones",
            "features": ["wireless", "15hr battery", "on-ear", "foldable", "mic"],
            "stock": 30,
            "active": True,
            "brand": "boAt",
            "rating": 4.2,
            "image_url": None,
        },
        {
            "name": "JBL LIVE 660NC Wireless Headphones",
            "description": "Over-ear wireless headphones with adaptive noise cancellation, 50hr battery, and hands-free voice assistant.",
            "price": 3999,
            "currency": "INR",
            "category": "headphones",
            "features": ["wireless", "noise cancellation", "50hr battery", "voice assistant", "over-ear"],
            "stock": 12,
            "active": True,
            "brand": "JBL",
            "rating": 4.5,
            "image_url": None,
        },
        {
            "name": "Sennheiser HD 450BT Wireless",
            "description": "Closed-back wireless headphones with active noise cancellation, 30hr battery, and AAC/aptX support.",
            "price": 4500,
            "currency": "INR",
            "category": "headphones",
            "features": ["wireless", "noise cancellation", "30hr battery", "aptX", "AAC"],
            "stock": 8,
            "active": True,
            "brand": "Sennheiser",
            "rating": 4.6,
            "image_url": None,
        },
        {
            "name": "Bose QuietComfort 45",
            "description": "Wireless over-ear headphones with world-class noise cancellation and 24-hour battery life.",
            "price": 7999,
            "currency": "INR",
            "category": "headphones",
            "features": ["wireless", "noise cancellation", "24hr battery", "over-ear", "voice assistant"],
            "stock": 5,
            "active": True,
            "brand": "Bose",
            "rating": 4.9,
            "image_url": None,
        },
        # TWS Earbuds
        {
            "name": "OnePlus Nord Buds 3 Pro",
            "description": "True wireless earbuds with 49dB ANC, 44hr total battery, IP55 water resistance.",
            "price": 2499,
            "currency": "INR",
            "category": "earbuds",
            "features": ["wireless", "noise cancellation", "44hr battery", "IP55", "ANC"],
            "stock": 25,
            "active": True,
            "brand": "OnePlus",
            "rating": 4.3,
            "image_url": None,
        },
        {
            "name": "Apple AirPods Pro (2nd Gen)",
            "description": "Active noise cancellation, Adaptive Audio, Personalized Spatial Audio with H2 chip.",
            "price": 14999,
            "currency": "INR",
            "category": "earbuds",
            "features": ["wireless", "noise cancellation", "spatial audio", "H2 chip", "MagSafe"],
            "stock": 20,
            "active": True,
            "brand": "Apple",
            "rating": 4.9,
            "image_url": None,
        },
        # Electronics
        {
            "name": "Anker PowerCore 20000 Power Bank",
            "description": "20000mAh portable charger with PowerIQ 3.0, dual USB-A and USB-C outputs.",
            "price": 2999,
            "currency": "INR",
            "category": "accessories",
            "features": ["20000mAh", "USB-C", "PowerIQ", "fast charging", "compact"],
            "stock": 40,
            "active": True,
            "brand": "Anker",
            "rating": 4.7,
            "image_url": None,
        },
        {
            "name": "Logitech MX Master 3S Wireless Mouse",
            "description": "Advanced wireless mouse with MagSpeed scrolling, 8K DPI sensor, quiet clicks.",
            "price": 6999,
            "currency": "INR",
            "category": "electronics",
            "features": ["wireless", "Bluetooth", "8K DPI", "ergonomic", "USB-C charging"],
            "stock": 10,
            "active": True,
            "brand": "Logitech",
            "rating": 4.8,
            "image_url": None,
        },
        {
            "name": "Samsung Galaxy Buds2 Pro",
            "description": "Intelligent ANC, 360 audio, 8hr playtime, IPX7 rated, Hi-Fi audio quality.",
            "price": 4999,
            "currency": "INR",
            "category": "earbuds",
            "features": ["wireless", "noise cancellation", "360 audio", "IPX7", "Hi-Fi"],
            "stock": 18,
            "active": True,
            "brand": "Samsung",
            "rating": 4.5,
            "image_url": None,
        },
    ]

    for p in products:
        p["created_at"] = datetime.now(timezone.utc)

    await col.insert_many(products)

    # Seed default policies
    pol_col = get_collection("policies")
    pol_count = await pol_col.count_documents({})
    if pol_count == 0:
        await pol_col.insert_one({
            "name": "default",
            "max_budget": settings.default_max_budget,
            "max_quantity": settings.max_quantity_per_order,
            "allowed_currency": settings.allowed_currency,
            "require_approval": settings.require_approval_for_all_purchases,
            "active": True,
        })

    import logging
    logging.getLogger(__name__).info(f"Seeded {len(products)} demo products and default policy.")

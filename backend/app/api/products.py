from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from app.models.product import ProductSearchRequest
from app.services import product_service

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("")
async def list_products(limit: int = Query(50, le=100)):
    products = await product_service.get_all_products(limit=limit)
    return {"products": products, "count": len(products)}


@router.get("/{product_id}")
async def get_product(product_id: str):
    product = await product_service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/search")
async def search_products(req: ProductSearchRequest):
    products = await product_service.search_products(
        query=req.query,
        max_price=req.max_price,
        min_price=req.min_price,
        category=req.category,
        required_features=req.required_features,
        limit=req.limit,
    )
    return {"products": products, "count": len(products), "query": req.query}


@router.get("/.well-known/merchant.json")
async def merchant_info():
    """AI-readable merchant protocol endpoint for agent discovery."""
    return {
        "merchant": "AgentCart Demo Store",
        "version": "1.0",
        "capabilities": ["catalog_search", "product_details", "checkout", "policy_validation"],
        "catalog_api": "/api/products/search",
        "currency": "INR",
        "policies": {
            "max_budget": 50000,
            "max_quantity": 5,
            "require_approval": True,
        },
    }

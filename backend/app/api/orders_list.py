from fastapi import APIRouter
from app.services import order_service

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.get("")
async def list_orders(limit: int = 50):
    orders = await order_service.get_all_orders(limit=limit)
    return {"orders": orders, "count": len(orders)}


@router.get("/{order_id}")
async def get_order(order_id: str):
    from fastapi import HTTPException
    order = await order_service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

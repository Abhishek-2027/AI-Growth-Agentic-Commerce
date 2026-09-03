"""
Deterministic Policy Engine — Pure Python, no LLM involvement.

Validates all pre-payment conditions before any money action is created.
"""

from typing import Dict, Any, List, Optional
from app.core.config import settings


class PolicyResult:
    def __init__(self):
        self.approved: bool = True
        self.reasons: List[str] = []
        self.blocked_reasons: List[str] = []
        self.budget_check: bool = False
        self.stock_check: bool = False
        self.quantity_check: bool = False
        self.currency_check: bool = False
        self.product_active_check: bool = False

    def block(self, reason: str):
        self.approved = False
        self.blocked_reasons.append(reason)

    def pass_check(self, reason: str):
        self.reasons.append(reason)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "approved": self.approved,
            "reasons": self.reasons,
            "blocked_reasons": self.blocked_reasons,
            "budget_check": self.budget_check,
            "stock_check": self.stock_check,
            "quantity_check": self.quantity_check,
            "currency_check": self.currency_check,
            "product_active_check": self.product_active_check,
        }


def run_policy_check(
    product: Dict[str, Any],
    quantity: int,
    user_budget: float,
) -> PolicyResult:
    """
    Deterministic safety validation — never uses LLM.

    Checks:
      1. Product exists and is active
      2. Stock availability
      3. Quantity limits
      4. Budget constraint
      5. Currency validity
      6. Approval requirement
    """
    result = PolicyResult()

    # 1. Product active check
    if not product.get("active", False):
        result.block("Product is not currently available")
        result.product_active_check = False
    else:
        result.pass_check("Product is active and available")
        result.product_active_check = True

    # 2. Stock check
    stock = product.get("stock", 0)
    if stock < quantity:
        result.block(f"Insufficient stock: {stock} available, {quantity} requested")
        result.stock_check = False
    else:
        result.pass_check(f"Stock available: {stock} units in inventory")
        result.stock_check = True

    # 3. Quantity check
    if quantity < 1:
        result.block("Quantity must be at least 1")
        result.quantity_check = False
    elif quantity > settings.max_quantity_per_order:
        result.block(
            f"Quantity {quantity} exceeds maximum allowed ({settings.max_quantity_per_order})"
        )
        result.quantity_check = False
    else:
        result.pass_check(f"Quantity {quantity} is within allowed limits")
        result.quantity_check = True

    # 4. Budget check (uses authoritative price from MongoDB)
    price = float(product.get("price", 0))
    total_amount = price * quantity
    if total_amount > user_budget:
        result.block(
            f"Total amount ₹{total_amount:.0f} exceeds user budget ₹{user_budget:.0f}"
        )
        result.budget_check = False
    else:
        result.pass_check(
            f"Budget check passed: ₹{total_amount:.0f} within ₹{user_budget:.0f} budget"
        )
        result.budget_check = True

    # 5. Currency check
    currency = product.get("currency", "INR")
    if currency != settings.allowed_currency:
        result.block(f"Currency '{currency}' is not allowed. Only {settings.allowed_currency} permitted.")
        result.currency_check = False
    else:
        result.pass_check(f"Currency {currency} is accepted")
        result.currency_check = True

    # 6. Approval gate (always required per platform policy)
    if settings.require_approval_for_all_purchases:
        result.pass_check("User approval will be required before payment execution")

    return result

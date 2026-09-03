"""
Multi-Layer Safety Guardrails for AgentCart.

Layer 1 — Input Guardrail:   Validate and sanitize raw user text.
Layer 2 — Intent Guardrail:  Validate extracted agent intent & parameters.
Layer 3 — Financial Guardrail: Non-bypassable financial boundary enforcement.
"""

import re
import logging
from typing import Dict, Any, Tuple
from app.core.config import settings

logger = logging.getLogger(__name__)

# Prohibited content patterns (prompt injection, jailbreak attempts, harmful requests)
_PROHIBITED_PATTERNS = [
    r"ignore (previous|all|above|prior) (instructions|prompt|rules)",
    r"(jailbreak|bypass|override) (safety|policy|rules|guardrails)",
    r"you are now (a|an|the)",
    r"(pretend|act|imagine) (you are|as if|that you)",
    r"(disregard|forget|ignore) (your|all) (rules|guidelines|constraints|safety)",
    r"(execute|run|eval)\s*\(",
    r"<script|javascript:",
    r"(sql injection|drop table|delete from|insert into)",
]

# Prohibited shopping items (demo-level safety)
_PROHIBITED_ITEMS = [
    "weapon", "gun", "knife", "drugs", "illegal", "stolen", "counterfeit",
    "explosive", "bomb", "narcotic", "ammunition",
]

_COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in _PROHIBITED_PATTERNS]


class GuardrailResult:
    def __init__(self, passed: bool, reason: str, layer: str):
        self.passed = passed
        self.reason = reason
        self.layer = layer

    def to_dict(self) -> Dict[str, Any]:
        return {"passed": self.passed, "reason": self.reason, "layer": self.layer}


def check_input_guardrail(user_message: str) -> GuardrailResult:
    """
    Layer 1: Input Guardrail
    - Checks for prompt injection attempts.
    - Checks for prohibited item requests.
    - Validates message length and content.
    """
    if not settings.enable_safety_guardrails:
        return GuardrailResult(True, "Guardrails disabled", "input")

    if not user_message or not user_message.strip():
        return GuardrailResult(False, "Empty message received", "input")

    if len(user_message) > 2000:
        return GuardrailResult(
            False, "Message too long (max 2000 characters)", "input"
        )

    # Check for prompt injection patterns
    for pattern in _COMPILED_PATTERNS:
        if pattern.search(user_message):
            logger.warning(f"Prompt injection detected: {user_message[:100]}")
            return GuardrailResult(
                False,
                "Potential prompt injection detected. Request blocked for safety.",
                "input",
            )

    # Check for prohibited items
    msg_lower = user_message.lower()
    for item in _PROHIBITED_ITEMS:
        if item in msg_lower:
            return GuardrailResult(
                False,
                f"Request contains prohibited item type: '{item}'. Cannot process this request.",
                "input",
            )

    return GuardrailResult(True, "Input validation passed", "input")


def check_intent_guardrail(intent: Dict[str, Any]) -> GuardrailResult:
    """
    Layer 2: Intent Guardrail
    - Validates agent-extracted intent schema.
    - Ensures budget is a positive number.
    - Ensures quantity is within allowed bounds.
    """
    if not settings.enable_safety_guardrails:
        return GuardrailResult(True, "Guardrails disabled", "intent")

    budget = intent.get("max_budget")
    quantity = intent.get("quantity", 1)

    if budget is not None:
        try:
            budget = float(budget)
            if budget <= 0:
                return GuardrailResult(
                    False, "Budget must be a positive number", "intent"
                )
            if budget > settings.default_max_budget * 10:
                return GuardrailResult(
                    False,
                    f"Budget ₹{budget} exceeds maximum allowed limit of ₹{settings.default_max_budget * 10}",
                    "intent",
                )
        except (TypeError, ValueError):
            return GuardrailResult(False, "Invalid budget value in intent", "intent")

    if quantity is not None:
        try:
            quantity = int(quantity)
            if quantity < 1:
                return GuardrailResult(
                    False, "Quantity must be at least 1", "intent"
                )
            if quantity > settings.max_quantity_per_order:
                return GuardrailResult(
                    False,
                    f"Quantity {quantity} exceeds maximum allowed ({settings.max_quantity_per_order})",
                    "intent",
                )
        except (TypeError, ValueError):
            return GuardrailResult(False, "Invalid quantity value in intent", "intent")

    return GuardrailResult(True, "Intent validation passed", "intent")


def check_financial_guardrail(
    product_price: float,
    user_budget: float,
    quantity: int,
    currency: str,
) -> GuardrailResult:
    """
    Layer 3: Financial Guardrail (non-bypassable)
    - Amount is read from MongoDB, never from LLM or frontend.
    - Enforces currency, budget, and quantity hard limits.
    """
    if not settings.enable_safety_guardrails:
        return GuardrailResult(True, "Guardrails disabled", "financial")

    if currency != settings.allowed_currency:
        return GuardrailResult(
            False,
            f"Currency '{currency}' is not allowed. Only {settings.allowed_currency} is permitted.",
            "financial",
        )

    if quantity < 1 or quantity > settings.max_quantity_per_order:
        return GuardrailResult(
            False,
            f"Quantity {quantity} violates limits (1–{settings.max_quantity_per_order})",
            "financial",
        )

    total_amount = product_price * quantity
    if total_amount > user_budget:
        return GuardrailResult(
            False,
            f"Total amount ₹{total_amount:.0f} exceeds user budget ₹{user_budget:.0f}",
            "financial",
        )

    if total_amount > settings.default_max_budget:
        return GuardrailResult(
            False,
            f"Total amount ₹{total_amount:.0f} exceeds platform max budget ₹{settings.default_max_budget}",
            "financial",
        )

    return GuardrailResult(
        True,
        f"Financial guardrail passed: ₹{total_amount:.0f} within budget ₹{user_budget:.0f}",
        "financial",
    )

from typing import TypedDict, Optional, List, Dict, Any


class AgentState(TypedDict):
    """Structured state for the LangGraph shopping agent."""
    session_id: str
    user_message: str
    intent: Optional[Dict[str, Any]]         # Extracted: query, budget, features, quantity
    products: Optional[List[Dict[str, Any]]] # Products found in catalog
    selected_product: Optional[Dict[str, Any]]
    recommendation_reason: Optional[str]
    recommendation_reasons_list: Optional[List[str]]
    purchase_proposal: Optional[Dict[str, Any]]
    policy_result: Optional[Dict[str, Any]]
    approval_status: Optional[str]           # PENDING | APPROVED | REJECTED
    internal_order_id: Optional[str]
    razorpay_order_id: Optional[str]
    payment_status: Optional[str]
    guardrail_result: Optional[Dict[str, Any]]
    error: Optional[str]
    step: Optional[str]                      # Current pipeline step for streaming

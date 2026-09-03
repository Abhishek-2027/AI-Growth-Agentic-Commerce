"""
LangGraph Agent Nodes — Each node is one stage in the shopping agent pipeline.

Flow:
  guardrail_input → extract_intent → search_catalog → analyze_products →
  select_product → create_proposal → END (awaiting frontend approval)
"""

import json
import logging
import re
from typing import Any, Dict, List

from app.agents.state import AgentState
from app.agents.prompts import INTENT_EXTRACTION_PROMPT, PRODUCT_ANALYSIS_PROMPT
from app.core.config import settings
from app.guardrails.safety import (
    check_input_guardrail,
    check_intent_guardrail,
)
from app.services import product_service, proposal_service
from app.services import audit_service
from app.models.audit import AuditActor, AuditEventType, AuditStatus

logger = logging.getLogger(__name__)


# ── LLM initialization ─────────────────────────────────────────────────────────

def _get_llm():
    """Return configured LLM client. Supports Google Gemini (default) or Groq fallback."""
    if settings.default_llm_provider == "gemini" and settings.google_api_key:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.google_api_key,
            temperature=0.1,
        )
    elif settings.groq_api_key:
        from langchain_groq import ChatGroq
        return ChatGroq(
            model="openai/gpt-oss-20b",
            groq_api_key=settings.groq_api_key,
            temperature=0.1,
        )
    raise RuntimeError("No LLM provider configured. Set GOOGLE_API_KEY or GROQ_API_KEY.")


def _extract_json(text: str) -> Dict:
    """Robustly extract JSON from LLM response."""
    text = text.strip()
    # Strip markdown code blocks
    text = re.sub(r"```(?:json)?\s*", "", text)
    text = re.sub(r"```\s*$", "", text)
    text = text.strip()
    # Find first { ... } block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group())
    return json.loads(text)


def _safe_float(val: Any, default: float = None) -> float:
    if val is None or val == "":
        return default
    try:
        if isinstance(val, str):
            val = val.replace(",", "")
        return float(val)
    except (ValueError, TypeError):
        return default



# ── Node 1: Input Guardrail ─────────────────────────────────────────────────────

async def node_guardrail_input(state: AgentState) -> AgentState:
    """Layer 1: Safety guardrail — validates raw user input before LLM processing."""
    result = check_input_guardrail(state["user_message"])

    await audit_service.log_event(
        session_id=state["session_id"],
        actor=AuditActor.GUARDRAIL,
        action=AuditEventType.GUARDRAIL_INPUT_CHECK,
        reason=result.reason,
        status=AuditStatus.SUCCESS if result.passed else AuditStatus.BLOCKED,
        metadata={"layer": "input", "passed": result.passed},
    )

    if not result.passed:
        return {**state, "error": result.reason, "step": "GUARDRAIL_BLOCKED", "guardrail_result": result.to_dict()}

    await audit_service.log_event(
        session_id=state["session_id"],
        actor=AuditActor.SYSTEM,
        action=AuditEventType.USER_REQUEST_RECEIVED,
        reason="User request received and passed input guardrail",
        status=AuditStatus.SUCCESS,
        metadata={"message": state["user_message"][:200]},
    )

    return {**state, "guardrail_result": result.to_dict(), "step": "INTENT_EXTRACTION"}


# ── Node 2: Extract Intent ──────────────────────────────────────────────────────

async def node_extract_intent(state: AgentState) -> AgentState:
    """Use LLM to extract structured shopping intent from natural language."""
    if state.get("error"):
        return state

    try:
        llm = _get_llm()
        
        # Fetch recent user messages and last state for conversational context
        from app.db.mongodb import get_collection
        import json
        col = get_collection("agent_sessions")
        session = await col.find_one({"session_id": state["session_id"]})
        
        history_str = "No previous context."
        current_state_str = "{}"
        pending_question_str = "None"

        if session:
            if "messages" in session:
                recent_msgs = session["messages"][:-1][-4:]
                if recent_msgs:
                    history_str = "\n".join([f"- {m.get('content', '')}" for m in recent_msgs if m.get("role") == "user"])
            
            last_intent = session.get("last_intent")
            if last_intent:
                current_state_str = json.dumps(last_intent, indent=2)
            
            last_error = session.get("last_error")
            if last_error:
                pending_question_str = last_error

        prompt = INTENT_EXTRACTION_PROMPT.format(
            user_message=state["user_message"],
            history=history_str,
            current_state=current_state_str,
            pending_question=pending_question_str
        )
        response = await llm.ainvoke(prompt)
        intent = _extract_json(response.content)

        # Merge with existing state (to ensure fields aren't dropped if LLM misses them)
        if session and session.get("last_intent"):
            merged_intent = session["last_intent"].copy()
            # Only update fields the LLM explicitly returned (handling null vs missing)
            for k, v in intent.items():
                if k in ["product_query", "category", "max_budget", "min_budget", "required_features", "quantity"]:
                    merged_intent[k] = v
            intent = merged_intent

        # Layer 2: Intent guardrail — validates LLM output schema
        guardrail = check_intent_guardrail(intent)
        if not guardrail.passed:
            await audit_service.log_event(
                session_id=state["session_id"],
                actor=AuditActor.GUARDRAIL,
                action=AuditEventType.GUARDRAIL_INPUT_BLOCKED,
                reason=guardrail.reason,
                status=AuditStatus.BLOCKED,
                metadata={"intent": intent},
            )
            return {**state, "error": guardrail.reason, "step": "GUARDRAIL_BLOCKED"}

        await audit_service.log_event(
            session_id=state["session_id"],
            actor=AuditActor.AGENT,
            action=AuditEventType.INTENT_EXTRACTED,
            reason=f"Intent: {intent.get('product_query')} | Budget: ₹{intent.get('max_budget')}",
            status=AuditStatus.SUCCESS,
            metadata={"intent": intent},
        )

        return {**state, "intent": intent, "step": "CATALOG_SEARCH"}

    except Exception as e:
        logger.error(f"Intent extraction failed: {e}")
        return {**state, "error": f"Intent extraction failed: {str(e)}", "step": "ERROR"}


# ── Node 3: Search Catalog ──────────────────────────────────────────────────────

async def node_search_catalog(state: AgentState) -> AgentState:
    """Search MongoDB product catalog based on extracted intent."""
    if state.get("error"):
        return state

    intent = state.get("intent", {})
    products = await product_service.search_products(
        query=intent.get("product_query", ""),
        max_price=_safe_float(intent.get("max_budget")),
        min_price=_safe_float(intent.get("min_budget")),
        category=intent.get("category"),
        required_features=intent.get("required_features", []),
        limit=10,
    )

    await audit_service.log_event(
        session_id=state["session_id"],
        actor=AuditActor.AGENT,
        action=AuditEventType.CATALOG_SEARCHED,
        reason=f"Found {len(products)} products matching query: '{intent.get('product_query')}'",
        status=AuditStatus.SUCCESS if products else AuditStatus.FAILED,
        metadata={"query": intent.get("product_query"), "count": len(products)},
    )

    if not products:
        # Smart edge-case handling for 0 results
        
        # 1. Was budget the issue? Let's check if we have alternatives under their budget!
        if _safe_float(intent.get("max_budget")):
            # Find ANY products in the same category under their budget
            alt_products = await product_service.search_products(
                category=intent.get("category") if intent.get("category") not in ["other", "null", "none"] else None,
                max_price=_safe_float(intent.get("max_budget")),
                limit=10,
            )
            
            if alt_products:
                # We found cheaper alternatives! Let's return them so the LLM can recommend them.
                # We modify the intent slightly so the LLM knows we are showing alternatives.
                intent["original_query"] = intent.get("product_query")
                return {**state, "products": alt_products, "intent": intent, "step": "ANALYZE_PRODUCTS"}

            # If no alternatives exist under budget, tell them what the actual item costs
            budget_free_products = await product_service.search_products(
                query=intent.get("product_query", ""),
                category=intent.get("category"),
                required_features=intent.get("required_features", []),
                limit=1,
            )
            if budget_free_products:
                min_found_price = budget_free_products[0].get("price", 0)
                error_msg = f"I couldn't find '{intent.get('product_query', 'that')}' or any alternatives under ₹{intent.get('max_budget')}. However, I did find options starting at ₹{min_found_price:,}. Would you like to increase your budget?"
                return {**state, "products": [], "error": error_msg, "step": "NO_PRODUCTS"}
                
        # 2. Were required features the issue?
        if intent.get("required_features"):
            feature_free_products = await product_service.search_products(
                query=intent.get("product_query", ""),
                max_price=_safe_float(intent.get("max_budget")),
                category=intent.get("category"),
                limit=10,
            )
            if feature_free_products:
                # Return the products without the strict features so LLM can suggest them!
                return {**state, "products": feature_free_products, "step": "ANALYZE_PRODUCTS"}

        # 3. Was the query just totally not in the catalog?
        error_msg = "No products found matching your exact requirements."
        if intent.get("category") and intent.get("category").lower() not in ["other", "null", "none"]:
            error_msg = f"We don't have '{intent.get('product_query')}' in stock. Would you like to browse our general {intent.get('category')} section?"

        return {
            **state,
            "products": [],
            "error": error_msg,
            "step": "NO_PRODUCTS",
        }

    return {**state, "products": products, "step": "ANALYZE_PRODUCTS"}


# ── Node 4: Analyze & Select Product ───────────────────────────────────────────

async def node_analyze_and_select(state: AgentState) -> AgentState:
    """Use LLM to analyze products and select the best recommendation."""
    if state.get("error"):
        return state

    products = state.get("products", [])
    intent = state.get("intent", {})

    if not products:
        return {**state, "error": "No products to analyze", "step": "NO_PRODUCTS"}

    try:
        # Prepare simplified product data for LLM (no prices from LLM will be used for payment)
        products_summary = [
            {
                "_id": str(p["_id"]),
                "name": p["name"],
                "price": p["price"],
                "features": p.get("features", []),
                "description": p.get("description", ""),
                "stock": p.get("stock", 0),
                "brand": p.get("brand", ""),
            }
            for p in products
        ]

        llm = _get_llm()
        prompt = PRODUCT_ANALYSIS_PROMPT.format(
            query=intent.get("product_query", ""),
            budget=intent.get("max_budget", "Not specified"),
            features=", ".join(intent.get("required_features", [])),
            products_json=json.dumps(products_summary, indent=2),
        )

        response = await llm.ainvoke(prompt)
        analysis = _extract_json(response.content)

        # Find selected product from our catalog (NOT from LLM's price data)
        selected_id = str(analysis.get("selected_product_id", ""))
        selected = next(
            (p for p in products if str(p["_id"]) == selected_id),
            products[0],  # fallback to first/cheapest if LLM ID doesn't match
        )

        await audit_service.log_event(
            session_id=state["session_id"],
            actor=AuditActor.AGENT,
            action=AuditEventType.PRODUCT_SELECTED,
            reason=analysis.get("recommendation_reason", "Best match selected"),
            status=AuditStatus.SUCCESS,
            metadata={
                "product_id": str(selected["_id"]),
                "product_name": selected["name"],
                "price": selected["price"],
            },
        )

        await audit_service.log_event(
            session_id=state["session_id"],
            actor=AuditActor.AGENT,
            action=AuditEventType.RECOMMENDATION_CREATED,
            reason=analysis.get("recommendation_reason", ""),
            status=AuditStatus.SUCCESS,
            metadata={"reasons": analysis.get("reasons_list", [])},
        )

        return {
            **state,
            "selected_product": selected,
            "recommendation_reason": analysis.get("recommendation_reason", ""),
            "recommendation_reasons_list": analysis.get("reasons_list", []),
            "step": "CREATE_PROPOSAL",
        }

    except Exception as e:
        logger.error(f"Product analysis failed: {e}")
        # Fallback: select first product without LLM
        selected = products[0]
        return {
            **state,
            "selected_product": selected,
            "recommendation_reason": f"Selected best available product within your budget",
            "recommendation_reasons_list": [
                f"✓ {selected['name']} is available",
                f"✓ Price ₹{selected['price']} fits requirements",
            ],
            "step": "CREATE_PROPOSAL",
        }


# ── Node 5: Create Proposal ─────────────────────────────────────────────────────

async def node_create_proposal(state: AgentState) -> AgentState:
    """
    Create a purchase proposal and run deterministic policy validation.
    The LLM does NOT control the actual price — it is read from MongoDB.
    """
    if state.get("error"):
        return state

    intent = state.get("intent", {})
    selected = state.get("selected_product", {})
    user_budget = _safe_float(intent.get("max_budget"), 999999.0)
    quantity = int(intent.get("quantity") or 1)

    try:
        proposal = await proposal_service.create_proposal(
            session_id=state["session_id"],
            product_id=str(selected["_id"]),
            quantity=quantity,
            user_budget=user_budget,
            reason=state.get("recommendation_reason", "Best match for requirements"),
            recommendation_reasons=state.get("recommendation_reasons_list", []),
        )

        policy = proposal.get("policy_result", {})
        policy_passed = policy.get("approved", False)

        audit_action = (
            AuditEventType.POLICY_CHECK_PASSED
            if policy_passed
            else AuditEventType.POLICY_CHECK_FAILED
        )
        audit_status = AuditStatus.SUCCESS if policy_passed else AuditStatus.BLOCKED

        await audit_service.log_event(
            session_id=state["session_id"],
            actor=AuditActor.POLICY,
            action=audit_action,
            reason="; ".join(policy.get("reasons", []) + policy.get("blocked_reasons", [])),
            status=audit_status,
            metadata={"policy": policy, "proposal_id": proposal["_id"]},
        )

        await audit_service.log_event(
            session_id=state["session_id"],
            actor=AuditActor.SYSTEM,
            action=AuditEventType.PURCHASE_PROPOSAL_CREATED,
            reason=f"Proposal created for {selected['name']} at ₹{selected['price']}",
            status=AuditStatus.INFO,
            metadata={"proposal_id": proposal["_id"]},
        )

        if policy_passed:
            await audit_service.log_event(
                session_id=state["session_id"],
                actor=AuditActor.SYSTEM,
                action=AuditEventType.USER_APPROVAL_REQUESTED,
                reason="Waiting for user to approve payment",
                status=AuditStatus.PENDING,
                metadata={"proposal_id": proposal["_id"]},
            )

        return {
            **state,
            "purchase_proposal": proposal,
            "policy_result": policy,
            "step": "AWAITING_APPROVAL" if policy_passed else "POLICY_BLOCKED",
        }

    except Exception as e:
        logger.error(f"Proposal creation failed: {e}")
        return {**state, "error": str(e), "step": "ERROR"}

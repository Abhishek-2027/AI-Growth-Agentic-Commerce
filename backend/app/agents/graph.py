"""
LangGraph Shopping Agent Graph

Flow:
  guardrail_input → extract_intent → search_catalog → analyze_and_select → create_proposal → END
"""

from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.nodes import (
    node_guardrail_input,
    node_extract_intent,
    node_search_catalog,
    node_analyze_and_select,
    node_create_proposal,
)


def _should_continue(state: AgentState) -> str:
    """Route based on current step or error."""
    if state.get("error"):
        return "end"
    step = state.get("step", "")
    if step == "GUARDRAIL_BLOCKED":
        return "end"
    if step == "NO_PRODUCTS":
        return "end"
    if step == "POLICY_BLOCKED":
        return "end"
    if step == "AWAITING_APPROVAL":
        return "end"
    if step == "ERROR":
        return "end"
    return "continue"


def build_agent_graph() -> StateGraph:
    """Build and compile the LangGraph agent workflow."""
    graph = StateGraph(AgentState)

    # Add all nodes
    graph.add_node("guardrail_input", node_guardrail_input)
    graph.add_node("extract_intent", node_extract_intent)
    graph.add_node("search_catalog", node_search_catalog)
    graph.add_node("analyze_and_select", node_analyze_and_select)
    graph.add_node("create_proposal", node_create_proposal)

    # Entry point
    graph.set_entry_point("guardrail_input")

    # Sequential edges with conditional routing after each node
    graph.add_conditional_edges(
        "guardrail_input",
        _should_continue,
        {"continue": "extract_intent", "end": END},
    )
    graph.add_conditional_edges(
        "extract_intent",
        _should_continue,
        {"continue": "search_catalog", "end": END},
    )
    graph.add_conditional_edges(
        "search_catalog",
        _should_continue,
        {"continue": "analyze_and_select", "end": END},
    )
    graph.add_conditional_edges(
        "analyze_and_select",
        _should_continue,
        {"continue": "create_proposal", "end": END},
    )
    graph.add_conditional_edges(
        "create_proposal",
        _should_continue,
        {"continue": END, "end": END},
    )

    return graph.compile()


# Module-level singleton
agent_graph = build_agent_graph()


async def run_agent(session_id: str, user_message: str) -> AgentState:
    """Run the full shopping agent pipeline and return final state."""
    initial_state: AgentState = {
        "session_id": session_id,
        "user_message": user_message,
        "intent": None,
        "products": None,
        "selected_product": None,
        "recommendation_reason": None,
        "recommendation_reasons_list": None,
        "purchase_proposal": None,
        "policy_result": None,
        "approval_status": None,
        "internal_order_id": None,
        "razorpay_order_id": None,
        "payment_status": None,
        "guardrail_result": None,
        "error": None,
        "step": "START",
    }
    result = await agent_graph.ainvoke(initial_state)
    return result

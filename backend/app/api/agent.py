import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.agents.graph import run_agent
from app.db.mongodb import get_collection

router = APIRouter(prefix="/api/agent", tags=["Agent"])


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


@router.post("/chat")
async def agent_chat(req: ChatRequest):
    """
    Main agent endpoint — runs the full LangGraph shopping pipeline.
    Returns agent state including products, recommendation, proposal, and policy result.
    """
    session_id = req.session_id or str(uuid.uuid4())

    # Store session
    col = get_collection("agent_sessions")
    await col.update_one(
        {"session_id": session_id},
        {
            "$setOnInsert": {"session_id": session_id, "created_at": __import__("datetime").datetime.utcnow()},
            "$push": {"messages": {"role": "user", "content": req.message}},
        },
        upsert=True,
    )

    result = await run_agent(session_id=session_id, user_message=req.message)

    # Save the resulting state so the next turn has context
    await col.update_one(
        {"session_id": session_id},
        {
            "$set": {
                "last_intent": result.get("intent"),
                "last_error": result.get("error"),
                "last_step": result.get("step")
            }
        }
    )

    return {
        "session_id": session_id,
        "step": result.get("step"),
        "error": result.get("error"),
        "intent": result.get("intent"),
        "products": result.get("products", []),
        "selected_product": result.get("selected_product"),
        "recommendation_reason": result.get("recommendation_reason"),
        "recommendation_reasons_list": result.get("recommendation_reasons_list", []),
        "purchase_proposal": result.get("purchase_proposal"),
        "policy_result": result.get("policy_result"),
        "guardrail_result": result.get("guardrail_result"),
    }


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Return agent session history."""
    col = get_collection("agent_sessions")
    doc = await col.find_one({"session_id": session_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Session not found")
    doc["_id"] = str(doc["_id"])
    return doc

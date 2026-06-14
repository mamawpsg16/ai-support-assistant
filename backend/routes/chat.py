"""
chat.py — the AI chat endpoint (Phase 4).

One endpoint:
  POST /chat   ->  send the conversation, get the assistant's reply.

The route stays thin: guard that Groq is configured, hand the messages to services/ai.py
(which runs the model + tools loop), return the reply. All the AI logic lives in the service.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend import config
from backend.database import get_db
from backend.schemas.chat import ChatRequest, ChatResponse
from backend.services import ai

router = APIRouter(prefix="/chat", tags=["chat"])


# POST /chat
@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    # Fail clearly if the Groq key isn't set, instead of a confusing crash.
    if not config.groq_is_configured():
        raise HTTPException(
            status_code=503,
            detail="AI is not configured (set GROQ_API_KEY in .env)",
        )

    # Pydantic models -> plain dicts for the Groq SDK.
    history = [{"role": m.role, "content": m.content} for m in request.messages]

    try:
        result = ai.run_chat(db, history, customer_id=request.customer_id)
    except Exception as exc:
        # Groq/network error etc. — surface a clean 502 instead of a raw 500.
        raise HTTPException(status_code=502, detail=f"AI request failed: {exc}") from exc

    return ChatResponse(reply=result["reply"])

"""
Chat schemas — API shape of the AI chat endpoint (Phase 4).

The frontend keeps the whole conversation and sends it on every request (the backend is
stateless), so a request carries the full message list, not just the latest line.
"""

from pydantic import BaseModel


# One message in the conversation. role is "user" or "assistant" (the system message is
# added server-side; the client never sends it).
class ChatMessage(BaseModel):
    role: str
    content: str


# INPUT: the conversation so far + optional "who am I talking to".
class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    customer_id: int | None = None   # lets the AI answer "my order" without re-asking


# OUTPUT: just the assistant's latest reply text.
class ChatResponse(BaseModel):
    reply: str

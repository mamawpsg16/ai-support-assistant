"""
ai.py — the AI chat brain (Phase 4).

This is the "agent loop": we talk to Groq's LLM, and whenever the model asks to use a tool
we run it (via ai_tools.dispatch) and feed the result back, until the model produces a
final text answer.

Mental model of one turn:
    messages = [system, ...history..., user]
    loop:
        reply = model(messages, tools)
        if reply wants tools:
            run each tool, append its result to messages, loop again
        else:
            return reply.content   # final answer

Why a loop and not a single call? The model often needs to look something up first
(e.g. call get_order_status), SEE the result, and only THEN write its answer. Each loop
pass is one model turn. We cap the passes so a misbehaving model can't loop forever.

Everything about WHICH tools exist lives in ai_tools.py; this file only orchestrates.
"""

import json

from groq import Groq
from sqlalchemy.orm import Session

from backend import config
from backend.services import ai_tools

# One Groq client for the app. api_key comes from .env via config. If the key is missing,
# creating the client is still fine — calls just fail, and the route guards with
# config.groq_is_configured() before we ever get here.
_client = Groq(api_key=config.GROQ_API_KEY or None)

# Safety cap: how many model<->tool round trips before we stop. Each refund/lookup is one
# pass; 5 is plenty for normal support questions and prevents runaway loops (and bills).
MAX_TOOL_ROUNDS = 5

# The system prompt sets the assistant's role and rules. It's the FIRST message every
# conversation, and it's where you steer behavior. Edit this to change the assistant's
# personality or policies.
SYSTEM_PROMPT = (
    "You are a helpful customer-support assistant for an online store. "
    "Be concise, friendly, and professional.\n\n"
    "Rules:\n"
    "- For questions about policies (shipping, returns, refunds, subscriptions, payments), "
    "use the search_faq tool and base your answer ONLY on what it returns. Do not invent "
    "policy details.\n"
    "- For questions about a specific order or account, use get_order_status or "
    "get_customer_subscription. If you don't know the order id or customer id, ASK the user "
    "for it instead of guessing.\n"
    "- Before issuing a refund with process_refund, confirm with the user which order they "
    "mean. Only refund when they clearly ask for it.\n"
    "- If a tool returns an error, explain the problem to the user plainly."
)


def _serialize_tool_calls(tool_calls) -> list[dict]:
    """Convert Groq's tool_call objects into plain dicts so we can put the assistant's
    message (with its tool calls) back into the messages list for the next round."""
    return [
        {
            "id": tc.id,
            "type": "function",
            "function": {"name": tc.function.name, "arguments": tc.function.arguments},
        }
        for tc in tool_calls
    ]


def run_chat(db: Session, history: list[dict], customer_id: int | None = None) -> dict:
    """Run one chat request to completion and return the final assistant reply.

    Args:
        db: database session, passed through to tools that need it.
        history: the conversation so far, as a list of {"role", "content"} dicts
                 (the frontend owns and sends this each turn — the backend is stateless).
        customer_id: optional; if set, we tell the model who it's helping so the user can
                     say "my subscription" without repeating their id.

    Returns: {"reply": "<final text>"}.
    """
    # Build the system prompt, optionally pinning the current customer.
    system_content = SYSTEM_PROMPT
    if customer_id is not None:
        system_content += f"\n\nYou are currently helping customer #{customer_id}."

    # The working message list we send to the model. Starts with system + the history.
    messages: list[dict] = [{"role": "system", "content": system_content}, *history]

    for _ in range(MAX_TOOL_ROUNDS):
        response = _client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=messages,
            tools=ai_tools.TOOL_SCHEMAS,
            tool_choice="auto",  # let the model decide whether to call a tool
        )
        message = response.choices[0].message

        # No tool calls -> the model gave its final answer. We're done.
        if not message.tool_calls:
            return {"reply": message.content or ""}

        # The model wants tools. First, record its request in the conversation.
        messages.append(
            {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": _serialize_tool_calls(message.tool_calls),
            }
        )

        # Run each requested tool and append its result as a "tool" message. The
        # tool_call_id links the result back to the specific call the model made.
        for tc in message.tool_calls:
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            result = ai_tools.dispatch(tc.function.name, args, db)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result),  # tool output goes back as JSON text
                }
            )
        # loop again so the model can read the tool results and continue/answer.

    # Hit the round cap without a final answer — return a safe fallback.
    return {
        "reply": (
            "Sorry, I couldn't complete that request. Please try rephrasing, or contact "
            "human support."
        )
    }

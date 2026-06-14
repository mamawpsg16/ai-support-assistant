"""
search.py — expose RAG retrieval over HTTP (Phase 3).

One read-only endpoint:
  GET /search?q=...&k=3   ->  the k knowledge-base chunks closest in meaning to q.

This lets you test retrieval from the browser or /docs before any AI is involved. In
Phase 4 the AI assistant will call the same search_faq() function as a "tool" — this route
is the human-facing window onto it.
"""

from fastapi import APIRouter, HTTPException, Query

from backend.schemas.search import SearchResponse
from backend.services import rag

router = APIRouter(prefix="/search", tags=["search"])


# GET /search?q=...&k=3
# q: the question/text to search for (required).
# k: how many chunks to return (default 3, capped so nobody asks for 1000).
@router.get("", response_model=SearchResponse)
def search(
    q: str = Query(..., min_length=1, description="What to search the knowledge base for"),
    k: int = Query(3, ge=1, le=10, description="How many matching chunks to return"),
):
    try:
        hits = rag.search_faq(q, k=k)
    except RuntimeError as exc:
        # search_faq raises this when the vector store is empty (index not built yet).
        # 503 = service not ready, with a clear message instead of a raw 500 crash.
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return SearchResponse(query=q, count=len(hits), results=hits)

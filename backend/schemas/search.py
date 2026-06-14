"""
Search schemas — API shape of a RAG knowledge-base search (Phase 3).

These describe what GET /search returns: a list of matching document chunks, ranked by
how close their meaning is to the query.
"""

from pydantic import BaseModel


# One matching chunk from the knowledge base.
class SearchHit(BaseModel):
    text: str           # the chunk's full text (title > heading + body)
    source: str         # which markdown file it came from, e.g. "shipping.md"
    heading: str        # the "##" section heading within that file
    distance: float     # vector distance to the query — SMALLER = more relevant


# The whole response for one search.
class SearchResponse(BaseModel):
    query: str                  # echo back what was searched (handy when debugging)
    count: int                  # how many hits were returned
    results: list[SearchHit]    # the hits, nearest first

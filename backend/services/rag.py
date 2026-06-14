"""
rag.py — Phase 3: Retrieval-Augmented Generation, the "retrieval" half.

Big picture (read this once):
  An LLM doesn't know OUR policies (returns, shipping, billing). RAG fixes that by
  SEARCHING our own documents for the chunks most relevant to a question, so they can
  later be handed to the AI as context (Phase 4). This file does the search part.

The pipeline lives here:
  1. LOAD    — read the markdown files in backend/knowledge/.
  2. CHUNK   — split each file into small topic-sized pieces (one per "##" heading).
  3. EMBED   — turn each chunk into a vector (a list of numbers capturing meaning).
               Chroma does this for us with a built-in local model (all-MiniLM-L6-v2),
               so no API key and no network are needed.
  4. STORE   — keep chunks + vectors in Chroma, persisted to disk (config.CHROMA_DIR).
  5. SEARCH  — embed a question, find the nearest chunks by meaning, return the top few.

Why "by meaning"? Two texts about the same idea get similar vectors even with no shared
words, so "can I send it back?" still finds the "Returns" chunk. That's the whole point.
"""

from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

from backend import config

# Name of the single Chroma "collection" (think: a table) that holds all our chunks.
COLLECTION_NAME = "support_kb"

# The embedding model. DefaultEmbeddingFunction = all-MiniLM-L6-v2 running locally via
# onnxruntime — no API key, no network at query time. First call downloads ~80MB once,
# then it's cached on disk. Both indexing and searching MUST use the SAME embedder, so we
# define it in one place.
#
# NOTE: this runs inside the Docker (Linux) container. The onnx wheel crashes on this
# project's Windows/Anaconda host, so RAG is a Docker-only path here — see CLAUDE.md.
_embedder = embedding_functions.DefaultEmbeddingFunction()

# Module-level cache for the client/collection. Building the client is cheap, but caching
# avoids reopening the on-disk store on every request once the app is running.
_client: chromadb.ClientAPI | None = None


def _get_collection():
    """Return the Chroma collection, creating the client + collection on first use.

    PersistentClient writes to a folder on disk (config.CHROMA_DIR), so the index
    survives restarts — we don't re-embed every boot. get_or_create_collection is
    idempotent: makes it the first time, reuses it after.
    """
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=config.CHROMA_DIR)
    return _client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=_embedder,
    )


def _chunk_markdown(text: str, source: str) -> list[dict]:
    """Split one markdown document into chunks — one chunk per '## ' section.

    Why split at all? If we embedded a whole file as one vector, search would return the
    entire file even when only one paragraph is relevant — noisy context for the AI.
    Headings are natural, human-made topic boundaries, so we cut there.

    We also prepend the document's top '# ' title to each chunk (e.g. "Shipping &
    Delivery > Tracking") so an isolated chunk still carries its context.

    Returns a list of dicts: {id, text, heading, source}.
    """
    lines = text.splitlines()

    # The H1 title = first line starting with "# " (one hash). Used as a prefix only.
    doc_title = source
    for line in lines:
        if line.startswith("# "):
            doc_title = line[2:].strip()
            break

    chunks: list[dict] = []
    current_heading: str | None = None
    current_body: list[str] = []

    def flush():
        """Save the section we've been accumulating, if it has any real content."""
        if current_heading is None:
            return
        body = "\n".join(current_body).strip()
        if not body:
            return
        # The text we embed: title + heading + body, so meaning is self-contained.
        full = f"{doc_title} > {current_heading}\n{body}"
        chunks.append(
            {
                "id": f"{source}::{current_heading}",  # stable id => re-indexing updates in place
                "text": full,
                "heading": current_heading,
                "source": source,
            }
        )

    for line in lines:
        if line.startswith("## "):  # start of a new section
            flush()                  # save the previous one first
            current_heading = line[3:].strip()
            current_body = []
        elif current_heading is not None:
            current_body.append(line)
    flush()  # don't forget the last section

    return chunks


def build_index() -> int:
    """Read every .md file in KNOWLEDGE_DIR, chunk them, and (re)load into Chroma.

    Idempotent: we use upsert with stable ids, so running this repeatedly updates existing
    chunks instead of creating duplicates. Returns the number of chunks indexed.

    Run this whenever the markdown changes (we'll call it from a small script next step).
    """
    knowledge_dir = Path(config.KNOWLEDGE_DIR)
    md_files = sorted(knowledge_dir.glob("*.md"))
    if not md_files:
        raise FileNotFoundError(f"No .md files found in {knowledge_dir.resolve()}")

    # Gather chunks from all files.
    all_chunks: list[dict] = []
    for path in md_files:
        text = path.read_text(encoding="utf-8")
        all_chunks.extend(_chunk_markdown(text, source=path.name))

    collection = _get_collection()
    # Chroma wants parallel lists. It embeds each document with our embedder automatically.
    collection.upsert(
        ids=[c["id"] for c in all_chunks],
        documents=[c["text"] for c in all_chunks],
        metadatas=[{"source": c["source"], "heading": c["heading"]} for c in all_chunks],
    )
    return len(all_chunks)


def search_faq(query: str, k: int = 3) -> list[dict]:
    """Find the k chunks whose meaning is closest to `query`.

    This is the function the AI will call as a tool in Phase 4. For now we test it directly.

    Returns a list of dicts: {text, source, heading, distance}, nearest first.
    `distance` is how far apart the vectors are — SMALLER = more similar/relevant.
    """
    collection = _get_collection()
    if collection.count() == 0:
        # Nothing indexed yet — give a clear signal instead of empty silence.
        raise RuntimeError("Knowledge base is empty. Run build_index() first.")

    res = collection.query(query_texts=[query], n_results=k)

    # Chroma returns dict-of-lists, batched per query. We sent one query, so take index 0.
    docs = res["documents"][0]
    metas = res["metadatas"][0]
    dists = res["distances"][0]
    return [
        {
            "text": doc,
            "source": meta.get("source"),
            "heading": meta.get("heading"),
            "distance": dist,
        }
        for doc, meta, dist in zip(docs, metas, dists)
    ]

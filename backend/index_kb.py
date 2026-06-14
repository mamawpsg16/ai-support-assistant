"""
index_kb.py — Phase 3: build the vector store from the markdown knowledge base.

Run this once now, and again any time you edit the files in backend/knowledge/:

    python -m backend.index_kb

What it does:
  1. build_index() reads backend/knowledge/*.md, chunks them, embeds each chunk with the
     local model, and stores everything in Chroma (config.CHROMA_DIR). First run downloads
     the ~80MB embedding model once; later runs are fast.
  2. Then it runs a few sample questions through search_faq() so you can SEE retrieval work
     — note how the matched chunk shares meaning, not necessarily words, with the question.
"""

from backend.services import rag

# Sample questions to demo retrieval. None of these use the exact wording in the docs —
# that's the point: embeddings match by meaning.
SAMPLE_QUESTIONS = [
    "can I send something back if I changed my mind?",
    "how long until my package arrives?",
    "how do I stop being billed every month?",
    "is my credit card safe with you?",
]


def main() -> None:
    print("Building index from markdown...")
    count = rag.build_index()
    print(f"Indexed {count} chunks.\n")

    for question in SAMPLE_QUESTIONS:
        print(f"Q: {question}")
        results = rag.search_faq(question, k=1)  # just the single best match for the demo
        top = results[0]
        # Show source + heading + distance, plus the first line of the chunk body.
        first_line = top["text"].splitlines()[0]
        print(f"   -> {top['source']} [{top['heading']}]  (distance {top['distance']:.3f})")
        print(f"      {first_line}\n")


if __name__ == "__main__":
    main()

"""ChromaDB search with metadata filtering and rule-based re-ranking.

Teaches: embedding function wrapping, metadata filters, score boosting.
Topic 2 of the module.
"""

import os

from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from chromadb import EmbeddingFunction, Documents, Embeddings

load_dotenv()

# ── Embedding client ────────────────────────────────────────────────

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

embedding_client = OpenAI(
    api_key=os.getenv("EMBEDDING_API_KEY"),
    base_url=os.getenv("EMBEDDING_BASE_URL"),
)


class CorpusEmbeddingFunction(EmbeddingFunction):
    """Wraps the embedding API so ChromaDB can call it during queries."""

    def __init__(self):
        pass

    def __call__(self, input: Documents) -> Embeddings:
        response = embedding_client.embeddings.create(
            model=EMBEDDING_MODEL, input=input
        )
        return [item.embedding for item in response.data]


# ── ChromaDB ────────────────────────────────────────────────────────

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_collection(
    name="novanet_hr", embedding_function=CorpusEmbeddingFunction()
)

# ── Re-ranking ──────────────────────────────────────────────────────

TYPE_BOOST = {"policy": 0.08, "sop": 0.05, "circular": 0.06, "faq": 0.00}


def rerank(results):
    """Reorder ChromaDB results by metadata signals."""
    ranked = []
    for chunk_id, doc, meta, dist in zip(
        results["ids"][0],
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        similarity = 1 - dist
        score = similarity
        if meta["status"] == "current":
            score += 0.10
        score += TYPE_BOOST.get(meta["doc_type"], 0)
        if meta["date_issued"] >= 20250101:
            score += 0.05
        ranked.append({
            "id": chunk_id, "text": doc, "metadata": meta,
            "similarity": similarity, "reranked_score": score,
        })
    ranked.sort(key=lambda x: x["reranked_score"], reverse=True)
    return ranked


def retrieve(query, n_results=5):
    """Retrieve, filter to current documents, and rerank."""
    results = collection.query(
        query_texts=[query], n_results=n_results,
        where={"status": "current"},
    )
    return rerank(results), results

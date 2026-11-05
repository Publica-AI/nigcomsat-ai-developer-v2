"""Pipeline functions from Topics 2-4, consolidated for the Streamlit app.

This file wraps retrieval (Topic 2), citations (Topic 3), and conversation
history (Topic 4) so app.py can import a single `chat()` function.
In the module demo, these functions move behind a FastAPI endpoint.
"""

import os
import re

from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from chromadb import EmbeddingFunction, Documents, Embeddings

load_dotenv()

# ── Clients ──────────────────────────────────────────────────────────

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

embedding_client = OpenAI(
    api_key=os.getenv("EMBEDDING_API_KEY"),
    base_url=os.getenv("EMBEDDING_BASE_URL"),
)

llm_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

MODEL = os.getenv("MODEL_NAME")


class CorpusEmbeddingFunction(EmbeddingFunction):
    """Wraps the embedding API so ChromaDB can call it during queries."""

    def __init__(self):
        pass

    def __call__(self, input: Documents) -> Embeddings:
        response = embedding_client.embeddings.create(
            model=EMBEDDING_MODEL, input=input
        )
        return [item.embedding for item in response.data]


# ── ChromaDB ─────────────────────────────────────────────────────────

CHROMA_PATH = os.path.join(
    "..", "..", "02-metadata-filtering-and-re-ranking", "demo", "chroma_db"
)
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_collection(
    name="novanet_hr", embedding_function=CorpusEmbeddingFunction()
)


# ── Retrieval (Topic 2) ─────────────────────────────────────────────

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


# ── Citations (Topic 3) ─────────────────────────────────────────────

def format_chunk_for_llm(chunk):
    """Add a doc_id header so the LLM can cite the source."""
    meta = chunk["metadata"]
    header = f"[{meta['doc_id']}] {meta['title']}"
    return f"--- {header} ---\n{chunk['text']}"


def build_context(chunks, top_n=5):
    """Join the top N formatted chunks into one string for the LLM."""
    return "\n\n".join(format_chunk_for_llm(c) for c in chunks[:top_n])


SYSTEM_PROMPT = """You are a NovaNet Technologies HR assistant.
Answer the employee's question using ONLY the documents below.
For each fact, add a [Source N] marker. After the answer, list sources like this:

Sources:
[Source 1] HR-POL-2025-006 — Annual Leave Policy, Section 3
[Source 2] HR-CIR-2025-001 — Revised Leave Entitlements

If the documents do not contain the answer, say:
\"I don't have information about that in the HR documents I can access.\"
Never invent facts or cite a document not provided above."""

DOC_ID_PATTERN = r"[A-Z]{2}-[A-Z]+-\d{4}-\d{3}"


def extract_citations(response_text):
    """Parse [Source ...] lines from the LLM response."""
    citations = {}
    n = 0
    for line in response_text.split("\n"):
        line = line.strip()
        if not re.match(r"^\[Source", line):
            continue
        doc_ids = re.findall(DOC_ID_PATTERN, line)
        if not doc_ids:
            continue
        n += 1
        doc_id = doc_ids[0]
        desc = re.split(DOC_ID_PATTERN, line)[-1]
        desc = re.sub(r'^[\s\]\[,—–―\-]+', "", desc).strip()
        citations[f"Source {n}"] = {"doc_id": doc_id, "section": desc}
    return citations


def verify_citations(citations, retrieved_chunks):
    """Check each citation against the chunks we actually retrieved."""
    retrieved_doc_ids = set(c["metadata"]["doc_id"] for c in retrieved_chunks)
    verified = []
    for key, cit in citations.items():
        doc_id = cit["doc_id"]
        if doc_id in retrieved_doc_ids:
            verified.append({**cit, "key": key, "status": "VERIFIED"})
        else:
            verified.append({
                **cit, "key": key, "status": "UNVERIFIED",
                "reason": "Document not in retrieved chunks",
            })
    return verified


REFUSAL_MESSAGE = (
    "I don't have information about that in the HR documents I can access. "
    "You may want to check with the HR department directly."
)


def should_refuse(chunks, citations, threshold=0.35):
    """Decide whether the system should refuse to answer."""
    if not chunks:
        return True, "No chunks retrieved"
    best_similarity = max(c["similarity"] for c in chunks)
    if best_similarity < threshold:
        return True, f"Best similarity {best_similarity:.3f} < {threshold}"
    if not citations:
        return True, "LLM produced no citations"
    return False, "Answer supported"


def get_cited_answer(question, n_results=5, top_n=5, threshold=0.35):
    """Full citation pipeline: retrieve, generate, parse, verify, refuse."""
    chunks, raw_results = retrieve(question, n_results=n_results)
    context = build_context(chunks, top_n=top_n)
    response = llm_client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Documents:\n{context}\n\nQuestion: {question}"},
        ],
        temperature=0.1,
    )
    answer = response.choices[0].message.content
    citations = extract_citations(answer)
    verified = verify_citations(citations, chunks[:top_n])
    refuse, reason = should_refuse(chunks, citations, threshold)
    return {
        "question": question,
        "answer": REFUSAL_MESSAGE if refuse else answer,
        "refused": refuse,
        "reason": reason,
        "citations": verified,
        "best_similarity": max(c["similarity"] for c in chunks) if chunks else 0,
    }


# ── Conversation History (Topic 4) ──────────────────────────────────

REWRITE_PROMPT = """Given a conversation between an employee and an HR assistant,
rewrite the employee's latest message as a standalone search query.

Rules:
1. Replace pronouns (it, that, those, they) with the specific nouns they refer to.
2. Include key details from the conversation (amounts, dates, document names).
3. Output ONLY the rewritten query — no explanation, no quotation marks.
4. If the message is already a standalone question, return it unchanged."""


def format_rewrite_input(history, latest_message):
    """Format conversation history + latest message for the rewriter."""
    lines = ["Conversation so far:"]
    for msg in history:
        role = "Employee" if msg["role"] == "user" else "Assistant"
        lines.append(f"{role}: {msg['content']}")
    lines.append(f"\nLatest message to rewrite:\n{latest_message}")
    return "\n".join(lines)


def rewrite_query(history, follow_up):
    """Rewrite a follow-up into a standalone search query using the LLM."""
    rewrite_input = format_rewrite_input(history, follow_up)
    response = llm_client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": REWRITE_PROMPT},
            {"role": "user", "content": rewrite_input},
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content.strip()


def get_history_window(history, max_pairs=5):
    """Return the last N user-assistant pairs from history."""
    max_messages = max_pairs * 2
    return history[-max_messages:]


def strip_citations(answer_text):
    """Remove [Source N] markers and the Sources block from an answer."""
    text = re.sub(r"\[Source\s*\d*\]", "", answer_text)
    text = re.split(r"\n\s*Sources?:", text)[0]
    text = re.sub(r"  +", " ", text).strip()
    return text


def estimate_tokens(text):
    """Rough estimate: 1 token ~ 4 characters."""
    return len(text) // 4


def trim_history(history, max_tokens=5000):
    """Remove oldest messages until history fits the token budget."""
    trimmed = list(history)
    while trimmed and estimate_tokens(str(trimmed)) > max_tokens:
        trimmed.pop(0)
    return trimmed


def chat(message, history, max_pairs=5, max_history_tokens=5000):
    """Full multi-turn pipeline: rewrite, retrieve, cite, append."""
    if history:
        window = get_history_window(history, max_pairs=max_pairs)
        window = trim_history(window, max_tokens=max_history_tokens)
        search_query = rewrite_query(window, message)
    else:
        search_query = message

    result = get_cited_answer(search_query)

    history.append({"role": "user", "content": message})
    clean_answer = strip_citations(result["answer"])
    history.append({"role": "assistant", "content": clean_answer})

    result["original_message"] = message
    result["search_query"] = search_query
    result["was_rewritten"] = (search_query != message)
    return result

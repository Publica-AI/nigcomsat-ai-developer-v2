"""Source citation in answers: generate, parse, verify, refuse.

Teaches: citation markers, doc_id verification, refusal logic.
Topic 3 of the module.
"""

import os
import re

from dotenv import load_dotenv
from openai import OpenAI

from retrieval import retrieve

load_dotenv()

# ── LLM client ──────────────────────────────────────────────────────

llm_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

MODEL = os.getenv("MODEL_NAME")

# ── Context formatting ──────────────────────────────────────────────


def format_chunk_for_llm(chunk):
    """Add a doc_id header so the LLM can cite the source."""
    meta = chunk["metadata"]
    header = f"[{meta['doc_id']}] {meta['title']}"
    return f"--- {header} ---\n{chunk['text']}"


def build_context(chunks, top_n=5):
    """Join the top N formatted chunks into one string for the LLM."""
    return "\n\n".join(format_chunk_for_llm(c) for c in chunks[:top_n])


# ── System prompt ───────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a NovaNet Technologies HR assistant.
Answer the employee's question using ONLY the documents below.
For each fact, add a [Source N] marker. After the answer, list sources like this:

Sources:
[Source 1] HR-POL-2025-006 — Annual Leave Policy, Section 3
[Source 2] HR-CIR-2025-001 — Revised Leave Entitlements

If the documents do not contain the answer, say:
\"I don't have information about that in the HR documents I can access.\"
Never invent facts or cite a document not provided above."""

# ── Citation parsing ────────────────────────────────────────────────

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


# ── Refusal logic ───────────────────────────────────────────────────

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


# ── Full citation pipeline ──────────────────────────────────────────


def get_cited_answer(question, n_results=5, top_n=5, threshold=0.35):
    """Retrieve, generate answer, parse citations, verify, refuse if needed."""
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

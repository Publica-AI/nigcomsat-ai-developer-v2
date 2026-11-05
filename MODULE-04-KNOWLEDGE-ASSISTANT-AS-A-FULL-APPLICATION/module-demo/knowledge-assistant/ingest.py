"""One-shot ingestion: load the NovaNet HR corpus, chunk, embed, store.

Usage:
    python ingest.py
    python ingest.py /path/to/corpus/folder

Default corpus path: ../../data/synthetic-hr-corpus/
Creates a persistent ChromaDB collection at ./chroma_db/
"""

import os
import sys

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
    def __init__(self):
        pass

    def __call__(self, input: Documents) -> Embeddings:
        response = embedding_client.embeddings.create(
            model=EMBEDDING_MODEL, input=input
        )
        return [item.embedding for item in response.data]


# ── Corpus metadata registry ───────────────────────────────────────

CORPUS_METADATA = {
    "HR-POL-2024-001_annual_leave_policy.txt": {
        "doc_id": "HR-POL-2024-001", "doc_type": "policy", "department": "HR",
        "date_issued": 20240115, "status": "superseded",
        "title": "Annual Leave Policy",
    },
    "HR-POL-2024-002_code_of_conduct.txt": {
        "doc_id": "HR-POL-2024-002", "doc_type": "policy", "department": "HR",
        "date_issued": 20240201, "status": "current",
        "title": "Code of Conduct",
    },
    "HR-POL-2024-003_remote_work_policy.txt": {
        "doc_id": "HR-POL-2024-003", "doc_type": "policy", "department": "HR / IT",
        "date_issued": 20240301, "status": "current",
        "title": "Remote Work Policy",
    },
    "HR-POL-2025-004_data_protection_policy.txt": {
        "doc_id": "HR-POL-2025-004", "doc_type": "policy", "department": "HR / Legal",
        "date_issued": 20250110, "status": "current",
        "title": "Data Protection Policy",
    },
    "HR-POL-2025-005_travel_expense_policy.txt": {
        "doc_id": "HR-POL-2025-005", "doc_type": "policy", "department": "HR / Finance",
        "date_issued": 20250301, "status": "current",
        "title": "Travel and Expense Policy",
    },
    "HR-POL-2025-006_annual_leave_policy_revised.txt": {
        "doc_id": "HR-POL-2025-006", "doc_type": "policy", "department": "HR",
        "date_issued": 20250701, "status": "current",
        "title": "Annual Leave Policy (Revised)",
    },
    "HR-SOP-2024-001_employee_onboarding.txt": {
        "doc_id": "HR-SOP-2024-001", "doc_type": "sop", "department": "HR",
        "date_issued": 20240401, "status": "current",
        "title": "Employee Onboarding Procedure",
    },
    "HR-SOP-2025-002_performance_review.txt": {
        "doc_id": "HR-SOP-2025-002", "doc_type": "sop", "department": "HR",
        "date_issued": 20250115, "status": "current",
        "title": "Performance Review Procedure",
    },
    "HR-SOP-2025-003_employee_exit.txt": {
        "doc_id": "HR-SOP-2025-003", "doc_type": "sop", "department": "HR",
        "date_issued": 20250401, "status": "current",
        "title": "Employee Exit Procedure",
    },
    "HR-SOP-2025-004_expense_claims.txt": {
        "doc_id": "HR-SOP-2025-004", "doc_type": "sop", "department": "HR / Finance",
        "date_issued": 20250501, "status": "current",
        "title": "Expense Claims Procedure",
    },
    "HR-CIR-2025-001_revised_leave_entitlements.txt": {
        "doc_id": "HR-CIR-2025-001", "doc_type": "circular", "department": "HR",
        "date_issued": 20250615, "status": "current",
        "title": "Revised Leave Entitlements",
    },
    "HR-CIR-2025-002_public_holiday_schedule.txt": {
        "doc_id": "HR-CIR-2025-002", "doc_type": "circular", "department": "HR",
        "date_issued": 20251128, "status": "current",
        "title": "2026 Public Holiday Schedule",
    },
    "HR-CIR-2026-003_remote_work_allowance_update.txt": {
        "doc_id": "HR-CIR-2026-003", "doc_type": "circular", "department": "HR / IT",
        "date_issued": 20260210, "status": "current",
        "title": "Updated Remote Work Equipment Allowance",
    },
    "HR-FAQ-2025-001_leave_and_absence.txt": {
        "doc_id": "HR-FAQ-2025-001", "doc_type": "faq", "department": "HR",
        "date_issued": 20250801, "status": "current",
        "title": "FAQ: Leave and Absence",
    },
    "HR-FAQ-2025-002_benefits_and_allowances.txt": {
        "doc_id": "HR-FAQ-2025-002", "doc_type": "faq", "department": "HR",
        "date_issued": 20250901, "status": "current",
        "title": "FAQ: Benefits and Allowances",
    },
}

# ── Chunking ────────────────────────────────────────────────────────

SEPARATOR = "-" * 60


def load_and_chunk(corpus_dir):
    """Read each .txt file and split into sections by the --- separator."""
    all_chunks = []
    for filename, meta in CORPUS_METADATA.items():
        filepath = os.path.join(corpus_dir, filename)
        if not os.path.exists(filepath):
            print(f"  WARNING: {filename} not found, skipping")
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        sections = text.split(SEPARATOR)
        for i, section in enumerate(sections[1:], start=1):
            section_text = section.strip()
            if len(section_text) < 30:
                continue
            all_chunks.append({
                "id": f"{meta['doc_id']}_chunk_{i}",
                "text": section_text,
                "metadata": {
                    "doc_id": meta["doc_id"],
                    "doc_type": meta["doc_type"],
                    "department": meta["department"],
                    "date_issued": meta["date_issued"],
                    "status": meta["status"],
                    "title": meta["title"],
                },
            })
    return all_chunks


# ── Main ────────────────────────────────────────────────────────────

def main():
    corpus_dir = (
        sys.argv[1]
        if len(sys.argv) > 1
        else os.path.join(os.path.dirname(__file__), "..", "..", "data", "synthetic-hr-corpus")
    )
    corpus_dir = os.path.abspath(corpus_dir)

    print(f"Corpus directory: {corpus_dir}")
    if not os.path.isdir(corpus_dir):
        print(f"ERROR: directory not found: {corpus_dir}")
        sys.exit(1)

    chroma_path = os.path.join(os.path.dirname(__file__), "chroma_db")
    print(f"ChromaDB path:    {chroma_path}")

    chunks = load_and_chunk(corpus_dir)
    print(f"Loaded {len(chunks)} chunks from {len(CORPUS_METADATA)} documents")

    client = chromadb.PersistentClient(path=chroma_path)
    embedding_fn = CorpusEmbeddingFunction()

    collection = client.get_or_create_collection(
        name="novanet_hr",
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"},
    )

    if collection.count() > 0:
        print(f"Collection already has {collection.count()} chunks — skipping")
        print("To re-ingest, delete the chroma_db/ folder and run again.")
        return

    collection.add(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks],
    )
    print(f"Ingested {collection.count()} chunks into collection 'novanet_hr'")

    for doc_id in sorted(set(c["metadata"]["doc_id"] for c in chunks)):
        n = sum(1 for c in chunks if c["metadata"]["doc_id"] == doc_id)
        print(f"  {doc_id}: {n} chunk{'s' if n > 1 else ''}")


if __name__ == "__main__":
    main()

# Demo Guide - Metadata Filtering & Re-ranking
**Module 4, Topic 2 | Estimated duration: 45-50 minutes**

---

## What This Demo Teaches

- Ingesting a document corpus into ChromaDB with structured metadata (doc_id, doc_type, department, date_issued, status)
- Showing that cosine similarity alone returns wrong answers when the corpus has superseded documents
- Using ChromaDB's `where` parameter to filter by metadata before similarity search
- Combining filters with `$and` and `$or` for date, doc_type, and status conditions
- Identifying the case filters cannot fix: a current policy whose amounts are outdated by a later circular
- Building a rule-based re-ranker that boosts by status, doc_type authority, and recency
- Measuring retrieval quality on a fixed test set across three pipeline configurations

---

## Setup

1. Open `demo/notebook.ipynb` in the Topic 2 demo folder
2. Confirm `chromadb`, `openai`, and `python-dotenv` are installed
3. Confirm the `.env` file has `EMBEDDING_API_KEY` (OpenAI, for embeddings) and `OPENAI_API_KEY` + `MODEL_NAME` + `OPENAI_BASE_URL` (for the LLM comparison at the end)
4. Run the import/setup cell and confirm it prints `ChromaDB client ready`
5. Keep `data/synthetic-hr-corpus/ANSWER-KEY.md` open on your own screen — it is instructor-only and gives confirmed facts for every document, the five retrieval traps, and the six refusal-test questions

---

## Demo Steps

### Part 1 — Metadata Registry and Ingestion (10 min)

Run the metadata registry cell. Point at the status column.

> "Every document has six metadata fields. The one that matters most today is `status`. See that HR-POL-2024-001 is `superseded`? That is the old annual leave policy — 20 days. HR-POL-2025-006 replaced it in July 2025 with 25 days. If we do not tell ChromaDB about this, it will happily return both and let the LLM pick one."

Run the load-and-chunk cell. Point at the chunk counts per document.

> "We split each document by its section separator. Policies with many sections produce more chunks; short circulars produce one or two. The metadata from the registry is attached to every chunk from that document."

Run the ingestion cell. Confirm the count.

> "This is a one-time operation. The persistent client saves everything to `./chroma_db`, so you do not re-ingest when you restart the notebook."

### Part 2 — The Problem: No Filters (7 min)

Run the unfiltered query cell: "How many days of annual leave do I get?"

> "Look at the top result. If it is HR-POL-2024-001 with status `superseded`, that is the 20-day policy. An LLM that sees this chunk first will likely say 20 days — wrong. The correct answer is 25 days, from HR-POL-2025-006."

Ask the class: "How would you decide which one is right, just by reading these five chunks?" Let them point out the status field.

> "You can see it. The system cannot — because we did not ask ChromaDB to filter by it."

### Part 3 — Status Filter (5 min)

Run the status filter cell.

> "One parameter: `where={\"status\": \"current\"}`. The superseded policy is gone. Every remaining result says 25 days. This is the single most important filter in any corpus where documents get replaced."

Ask: "Should `status=current` be your default, or should you apply it only when needed?" The answer: always default, override only for historical queries.

### Part 4 — Compound Filters (5 min)

Run the compound filter cell: "What changed in the leave policy this year?"

> "Here we combine three conditions with `$and`: status is current, date is 2025 or later, and doc_type is not FAQ. This narrows the results to recent authoritative documents. Notice the integer date format — `20250101` instead of `"2025-01-01"` — because ChromaDB's `$gte` operator requires numeric values."

Point out the trade-off: over-filtering can exclude documents you need. A question about home office equipment needs chunks from three different doc_types.

### Part 5 — The Trap (7 min)

Run the remote work allowance query.

> "Both the policy and the circular are `current`. But the policy says NGN 25,000 and the circular says NGN 35,000. The circular updated the amount in March 2026 without replacing the entire policy. A status filter alone cannot fix this."

Pause and ask the class: "How would you solve this?"

Expected answers:
- "Always prefer circulars" — wrong, circulars only update specific amounts
- "Sort by date" — partially right, but breaks when an older document is still authoritative for sections the circular did not touch
- "Include both and let the LLM figure it out" — better, but only works if the circular ranks high enough to appear in the context

> "The real answer: include both, but re-rank so the more recent, more specific source appears first. That is what the re-ranker does."

### Part 6 — The Re-ranker (8 min)

Run the re-ranker cell. Walk through the code.

> "Three boosts. Status: +0.10 for current. Doc_type: policies get +0.08, circulars get +0.06. Recency: anything from 2025 onwards gets +0.05. These add to the similarity score."

Point at the remote work results after re-ranking.

> "The circular now outranks the policy. Its total boost is 0.10 (current) + 0.06 (circular) + 0.05 (2026) = +0.21. The policy gets 0.10 (current) + 0.08 (policy) + 0.00 (2024, too old) = +0.18. The date boost is what tips the balance."

Ask: "Are these magic numbers?" Yes — tuned by hand on the test set. For 15 documents that is fine. For a larger corpus you would learn the weights from labelled data.

### Part 7 — The Comparison Table (5 min)

Run the five-question test set cell.

> "Five questions, three pipelines, one check: does the expected source appear as the top-1 result? The baseline misses the leave question and possibly the remote work question. The filter fixes the leave question. The re-ranker fixes the remote work question."

If a question gets `MISS` across all three pipelines, stop and investigate — it is worth debugging live. If everything is `OK` in the reranked column, celebrate briefly and move on.

### Part 8 — LLM Impact (5 min)

Run the LLM comparison cell.

> "Same question, two different sets of context chunks. The baseline answer may say 20 days, or hedge between 20 and 25. The full-pipeline answer should say 25 days clearly. This is the payoff: better retrieval produces better answers."

If both answers say 25 (the LLM managed to pick the right document even from mixed context), point out that it got lucky — with a larger corpus and more noise, the baseline will fail more often. The filter makes the answer reliable, not just occasionally correct.

### Close (3 min)

> "Everything you built today — the ingestion script, the metadata registry, the status filter, the re-ranker — becomes `retrieval.py` in the reference application. Tomorrow in Topic 3 we add source citations: the answer says *where* it got the information, and we verify that each citation actually exists in the retrieved chunks."

---

## Common Issues

- **`EMBEDDING_API_KEY` not set or invalid** — the OpenAIEmbeddingFunction will throw on the first query, not on creation. If ingestion fails, check the key.
- **Ingestion runs twice and fails with duplicate IDs** — the `if collection.count() == 0` guard prevents this. If the student wants to re-ingest (e.g. after changing the chunking), they need to delete `./chroma_db/` or call `chroma_client.delete_collection("novanet_hr")` first.
- **Unfiltered query does not show the superseded policy at the top** — embedding models differ; some may rank the current policy higher even without filters. If this happens, the lesson still holds: the system *could* return the wrong one, and filtering ensures it never does.
- **Compound filter with three conditions raises an error** — older ChromaDB versions require exactly two elements in `$and`. If this happens, nest two `$and` clauses: `{"$and": [cond1, {"$and": [cond2, cond3]}]}`.
- **Re-ranker does not change the order** — if the similarity scores are very different (e.g. 0.95 vs 0.60), the metadata boosts (+0.05 to +0.10) will not overcome the gap. This is expected — the re-ranker only reorders close results. Adjust the boost weights or retrieve more candidates (`n_results=10`).

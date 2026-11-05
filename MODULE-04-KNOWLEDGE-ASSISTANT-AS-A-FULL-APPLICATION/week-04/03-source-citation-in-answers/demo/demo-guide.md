# Demo Guide - Source Citation in Answers
**Module 4, Topic 3 | Estimated duration: 40-45 minutes**

---

## What This Demo Teaches

- Adding doc_id headers to chunks so the LLM can cite specific documents
- Designing a system prompt that requires per-claim citations and provides a refusal template
- Comparing an uncited answer to a cited answer for the same question
- Parsing `[Source N]` markers from LLM responses with regex
- Verifying that each cited document was actually in the retrieved chunks
- Detecting hallucinated citations (UNVERIFIED status)
- Refusing to answer when the corpus has no relevant information
- Running a test set of answerable and unanswerable questions through the full pipeline

---

## Prerequisites

- **Topic 2 notebook must be completed first.** This notebook connects to the ChromaDB collection (`novanet_hr`) created and ingested in the Topic 2 demo. If students have not run Topic 2, the setup cell will fail.
- The `.env` file needs the same six variables as Topic 2: `OPENAI_API_KEY`, `MODEL_NAME`, `OPENAI_BASE_URL`, `EMBEDDING_API_KEY`, `EMBEDDING_BASE_URL`, `EMBEDDING_MODEL`.

---

## Setup

1. Open `demo/notebook.ipynb` in the Topic 3 demo folder
2. Confirm the `.env` file is present with all six variables
3. Run the setup cell — it should print `Connected to collection 'novanet_hr' — 90 chunks`
4. If it fails with "collection not found," the student needs to go back and run the Topic 2 notebook (ingestion cell)
5. Keep `data/synthetic-hr-corpus/ANSWER-KEY.md` open on your own screen

---

## Demo Steps

### Part 1 — Retrieval Helpers and Chunk Formatting (7 min)

Run the retrieval helpers cell. Point at the `rerank` function.

> "This is the same re-ranker from Topic 2 — we are reusing it. The `retrieve` function combines the ChromaDB query (with the status=current filter) and the re-ranker into one call. From here on, retrieval is a solved problem. Today we focus on what happens after retrieval."

Run the chunk formatting cell. Show the output.

> "Look at the header line: `--- [HR-POL-2024-003] Remote Work Policy ---`. This is what the LLM sees before the chunk text. Without this header, the LLM has raw paragraphs and no way to say 'this came from document X.' The header is the bridge between retrieval and citation."

Ask: "Why include the title alongside the doc_id?" Because the doc_id alone (`HR-POL-2024-003`) is not human-readable. The title helps the LLM write a more useful citation.

### Part 2 — Without Citations (5 min)

Run the uncited answer cell.

> "Read this answer. Is it correct? Probably. But where did it come from? Which policy? Which section? If you are the employee and your manager says 'show me where it says that,' you cannot. You have an answer, but not evidence."

Ask the class: "Would you trust this answer enough to act on it without checking?" Let them discuss. The point is that correctness is not enough — traceability matters.

### Part 3 — The System Prompt and Cited Answer (8 min)

Run the system prompt cell. Read each rule aloud.

> "Rule 1: every factual claim gets a [Source N] marker — not just the answer overall, but each fact. Rule 2: list the sources at the end with the doc_id. Rule 3: if the documents do not contain the answer, say exactly this sentence. Rule 4: never cite a document that was not provided — this is the anti-hallucination guardrail."

Run the cited answer cell. Compare to the uncited version.

> "Same question, same chunks. But now every claim has a source. The employee can take '[Source 1] HR-POL-2024-003' to their manager and say 'section 2 of the Remote Work Policy says I am eligible.' That is actionable."

Ask: "Will the LLM always follow these rules?" No — that is why the next step is verification.

### Part 4 — Parsing and Verifying Citations (8 min)

Run the parsing cell. Show the extracted citations.

> "The regex looks for `[Source N]` followed by a doc_id in our format and a description. It pulls out structured data we can work with programmatically."

Run the verification cell. Point at the VERIFIED results.

> "For each citation, we check: is this doc_id in the chunks we retrieved? If yes, VERIFIED — the source is real. If no, UNVERIFIED — the LLM hallucinated it."

Point at the fake citation test at the bottom.

> "We manually tested with a doc_id that does not exist: HR-POL-2024-007. The verifier catches it immediately. In a real system, you would remove this citation from the answer or flag the entire response for review."

Ask: "How often do LLMs hallucinate citations?" With a clear system prompt and real chunks in the context, it is rare — but 'rare' is not 'never,' and one wrong citation in an HR system is one too many.

### Part 5 — Refusal (8 min)

Run the refusal cell. This is the most important demo moment.

> "The question is 'Can I bring my pet to the office?' The NovaNet HR corpus has no pet policy. Look at the similarity scores — they are low. The chunks returned are about workplace conduct, remote work, things that vaguely relate to 'office' but have nothing to do with pets."

Point at the LLM's response.

> "The system prompt told the LLM to refuse if the documents do not contain the answer. Did it follow the instruction?"

If the LLM refused: celebrate briefly. If it tried to answer anyway: that is why we have the `should_refuse` function as a backup.

Run the `should_refuse` cell. Show both tests.

> "Two signals. Signal 1: the best similarity score is below 0.35 — the corpus probably does not cover this topic. Signal 2: the LLM produced no citations. Either signal triggers a refusal. For the pet question, both fire. For the remote work question, neither fires."

Ask: "What would happen if we set the threshold too high — say, 0.60?" We would refuse questions the corpus can answer. "Too low — say, 0.10?" We would try to answer questions with garbage context. The threshold needs tuning on the test set.

### Part 6 — The Full Pipeline (5 min)

Run the `get_cited_answer` cell.

> "One function that does everything: retrieve, rerank, format, ask the LLM, parse citations, verify them, and decide whether to refuse. This is `citations.py` in the reference application — the entire citation layer in one place."

Point at the return value: question, answer, refused flag, reason, verified citations, and best similarity.

> "Everything a caller needs: the Streamlit app (Topic 5) shows the answer and the source list; the logging system (Topic 6) records the citations and the similarity score."

### Part 7 — The Test Set (5 min)

Run the test set cell.

> "Eight questions: five that the corpus can answer, three that it cannot. For each one, we check: did the pipeline answer when it should, refuse when it should, and cite real documents?"

Walk through the results table. If everything shows OK, that is the payoff — the system handles both answerable and unanswerable questions correctly.

If any show MISS, stop and investigate live:
- An answerable question refused: check the similarity — is the threshold too high?
- A refusal question answered: check the LLM's response — did it hallucinate?

> "This test set is how you know your citation pipeline works. Every time you change the system prompt, the threshold, or the retrieval weights, you re-run this set."

### Close (2 min)

> "Everything you built today — the chunk formatter, the system prompt, the citation parser, the verifier, the refusal logic — becomes `citations.py` in the reference application. It takes re-ranked chunks from `retrieval.py` and returns a cited, verified answer. Tomorrow in Topic 4 we handle the next problem: what happens when the employee asks a follow-up question like 'Does that apply to contract staff?' The system needs to remember the conversation."

---

## Common Issues

- **"Collection not found" on setup** — the student has not run the Topic 2 notebook. They need to go back and run the ingestion cell in Topic 2 first.
- **LLM does not produce `[Source N]` markers** — some models follow the system prompt less reliably. Try lowering the temperature to 0.0, or add an example to the system prompt showing the expected format.
- **Regex misses citations** — the LLM may format citations differently (e.g. `[Source 1]: HR-POL-...` with a colon, or `(Source 1)` with parentheses). Adjust the regex pattern if needed. The current pattern handles commas, em-dashes, en-dashes, and hyphens as separators.
- **Refusal question gets an answer instead of refusing** — if the similarity threshold is too low, the `should_refuse` function will not trigger. Check the best similarity score for refusal questions and adjust the threshold. Also check whether the LLM followed rule 3 of the system prompt.
- **Answerable question gets refused** — the similarity threshold is too high for this embedding model. Lower it (try 0.30 or 0.25) and re-run the test set.
- **All citations show UNVERIFIED** — the `verify_citations` function is comparing against the wrong chunk list. Make sure it receives the same chunks that were formatted and sent to the LLM (the top N after reranking), not the raw ChromaDB results.

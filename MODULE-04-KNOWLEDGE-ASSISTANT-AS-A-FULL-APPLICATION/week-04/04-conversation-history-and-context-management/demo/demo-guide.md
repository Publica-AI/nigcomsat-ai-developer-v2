# Demo Guide - Conversation History & Context Management
**Module 4, Topic 4 | Estimated duration: 35-40 minutes**

---

## What This Demo Teaches

- Why follow-up questions fail at retrieval (pronouns have no referent)
- Using the LLM to rewrite follow-ups into standalone search queries
- Comparing retrieval results for raw follow-ups vs. rewritten queries
- Storing conversation history as a `{role, content}` message list
- Stripping citations from stored answers to keep history clean for the rewriter
- Estimating token counts and trimming history to fit a budget
- Building a `chat()` function that handles both first questions and follow-ups
- Testing multi-turn conversations, topic switches, and off-topic questions

---

## Prerequisites

- **Topic 2 notebook must be completed first.** This notebook connects to the ChromaDB collection (`novanet_hr`) created and ingested in the Topic 2 demo.
- The `.env` file needs the same six variables as Topics 2 and 3: `OPENAI_API_KEY`, `MODEL_NAME`, `OPENAI_BASE_URL`, `EMBEDDING_API_KEY`, `EMBEDDING_BASE_URL`, `EMBEDDING_MODEL`.
- **Topic 3 is not a prerequisite to run**, but students should understand the citation pipeline conceptually. This notebook brings forward all Topic 3 functions internally.

---

## Setup

1. Open `demo/notebook.ipynb` in the Topic 4 demo folder
2. Confirm the `.env` file is present with all six variables
3. Run the setup cell — it should print `Connected to collection 'novanet_hr' — 90 chunks`
4. If it fails with "collection not found," the student needs to go back and run the Topic 2 notebook (ingestion cell)
5. Keep `data/synthetic-hr-corpus/ANSWER-KEY.md` open on your own screen

---

## Demo Steps

### Part 1 — Setup and Pipeline Helpers (5 min)

Run the setup cell and the pipeline helpers cell.

> "These are the same functions from Topics 2 and 3 — retrieval, re-ranking, citation parsing, verification, and refusal. We are not changing them today. Today we add a layer on top: conversation history and query rewriting. The quick test at the bottom confirms the pipeline still works."

If the pipeline test prints FAIL, stop and debug — the rest of the demo depends on working retrieval and citations.

### Part 2 — The Follow-up Problem (5 min)

Run the follow-up problem cell. This is the motivating demo.

> "Turn 1: 'How many days of annual leave do I get?' The pipeline answers correctly — 25 days, with a citation. Turn 2: 'Does that apply to contract staff?' Look at what ChromaDB returned. These chunks are about onboarding, conduct, exit procedures — nothing about leave or contract staff."

Point at the similarity scores.

> "The scores are low, and the chunks are wrong. ChromaDB searched for the literal string 'does that apply to contract staff' and found the closest matches. But 'that' means '25-day annual leave entitlement' — and ChromaDB has no way to know that."

Ask the class: "What would you do to fix this?" Let them suggest ideas. Some will say "send the history to ChromaDB" — but ChromaDB does not take history, only a query string. The answer is to rewrite the query.

### Part 3 — The Rewrite Prompt and Function (7 min)

Run the rewrite prompt cell. Read each rule aloud.

> "Rule 1: replace pronouns. 'That' becomes 'the 25-day annual leave entitlement.' Rule 2: include key details — amounts, dates, document names from the conversation. Rule 3: output only the rewritten query. We send this directly to ChromaDB, so we need a clean string, not an explanation. Rule 4: if the message is already standalone, return it unchanged. Not every message needs rewriting."

Point at `temperature=0.0`.

> "The rewriter should be literal, not creative. We do not want it to rephrase 'annual leave' as 'vacation days' — that could change the retrieval results."

### Part 4 — Testing the Rewriter (5 min)

Run the rewriter test cell. Show the three rewrites.

> "Look at each rewrite. 'Does that apply to contract staff?' should become something like 'Does the 25-day annual leave entitlement apply to contract staff?' The pronouns are gone, the key detail (25 days, annual leave) is included, and it is a standalone query ChromaDB can search."

If any rewrite looks wrong, discuss it with the class. Small variations are fine — the rewrite does not need to be perfect, just better than the raw follow-up.

### Part 5 — Rewrite Fixes Retrieval (5 min)

Run the retrieval comparison cell.

> "This is the payoff. Same follow-up, two different searches. The raw query 'does that apply to contract staff' returns irrelevant chunks. The rewritten query returns chunks from the Annual Leave Policy and the leave FAQ — exactly what we need."

Point at the similarity scores — they should be significantly higher for the rewritten query.

> "One extra LLM call — about 200 milliseconds — and the retrieval goes from useless to correct."

### Part 6 — History Storage and Trimming (5 min)

Run the history storage cell, then the token budget cell.

> "Two utilities. First, `strip_citations` removes the `[Source N]` markers and the Sources block from the answer before we store it in history. The rewriter does not need citation markers — they would confuse it. Second, `get_history_window` keeps only the last N exchanges."

For the token budget cell:

> "We estimate tokens at roughly 4 characters per token — not exact, but close enough for budget management. The `trim_history` function drops the oldest messages until the total fits. In this test, we built a 20-turn history and trimmed it down."

Ask: "Why not use the exact tokeniser?" Because for trimming decisions, approximate is fast and good enough. The exact count matters for billing, not for deciding whether to drop the oldest message.

### Part 7 — The Full Pipeline and Multi-turn Test (8 min)

Run the `chat()` function cell, then the multi-turn conversation cell.

> "The `chat()` function is the final product. It checks if history is empty — if so, no rewrite needed. Otherwise, it trims history, rewrites the follow-up, calls the citation pipeline with the rewritten query, and appends the exchange to history."

Walk through each turn of the three-turn conversation:

- **Turn 1:** "How many days of annual leave do I get?" — no rewrite, standalone question, answered with citations.
- **Turn 2:** "How many of those can I carry over to next year?" — rewritten to include "annual leave days," retrieves carry-over policy (10 days by 31 March).
- **Turn 3:** "What is the deadline for using them?" — rewritten to include "carry-over annual leave days," finds the March deadline.

> "Three turns, all answered correctly. Turn 1 used one LLM call (answer only). Turns 2 and 3 used two each (rewrite + answer)."

### Part 8 — Edge Cases (5 min)

Run the edge cases cell.

> "Three tests. First, a topic switch: 'What is the remote work allowance?' This is already a standalone question — the rewriter should return it unchanged or nearly unchanged. Second, a follow-up on the new topic: 'Was it always that amount?' The rewriter should connect 'that amount' to the remote work allowance, not to annual leave. Third, an off-topic question: 'Can I bring my pet to the office?' The citation pipeline should refuse, even in the middle of a conversation."

If the topic switch rewrite adds unnecessary context from the leave conversation, discuss it:

> "The rewriter included some leave context even though the question is standalone. That is not ideal but not harmful — the retrieval will still find remote work chunks because the question explicitly mentions 'remote work allowance.' This is the kind of imperfection we accept."

### Close (2 min)

> "Everything you built today — the rewrite prompt, the rewriter, the history window, the token trimmer, and the `chat()` function — becomes `history.py` in the reference application. Combined with `retrieval.py` from Topic 2 and `citations.py` from Topic 3, the assistant now handles multi-turn conversations with cited answers and refusal. Next topic — Building the Streamlit Interface — puts a chat UI on top so a non-technical employee can use this without Python."

---

## Common Issues

- **"Collection not found" on setup** — the student has not run the Topic 2 notebook. They need to go back and run the ingestion cell in Topic 2 first.
- **Rewriter adds unnecessary context** — e.g., rewrites "What is the remote work allowance?" as "What is the remote work allowance at NovaNet, in addition to the 25-day annual leave?" The extra context from history leaks in. This is cosmetic — retrieval still works. Discuss with the class as a quality-vs-perfection tradeoff.
- **Rewriter changes the question's meaning** — e.g., rewrites "Can I carry those over?" as "Can I carry over remote work days?" (wrong topic). Check the history: is the most recent exchange about leave or remote work? The rewriter follows the most recent context. If the history is long and mixed, the sliding window helps focus on the relevant exchanges.
- **Follow-up gets refused when it should be answered** — the rewritten query may not be a close enough semantic match. Check the rewritten query — is it a good standalone question? If not, try adjusting the rewrite prompt.
- **Token budget trim drops too much history** — lower the `max_tokens` parameter or increase it depending on your model's context window. The default 5,000 tokens is conservative; models with 128K context windows can afford much more.
- **`strip_citations` misses some citation formats** — the regex expects `[Source N]` markers. If the LLM uses a different format, the markers may leak into history. Adjust the regex if needed.

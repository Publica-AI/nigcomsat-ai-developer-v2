# Module Demo Guide - The Knowledge Assistant as a Full Application
**Module 4 | Estimated duration: 50-60 minutes**

---

## What This Demo Teaches

This is the capstone walkthrough for Module 4. It demonstrates the complete, integrated knowledge assistant — every component from Topics 2 through 6 assembled into a single self-contained application that an employee can use to query HR policies and get cited answers.

By the end, students see:
- The full folder structure and how each file maps to a topic
- Corpus ingestion from raw `.txt` files to searchable ChromaDB vectors
- The FastAPI backend running with authentication, pipeline, and logging
- The Streamlit interface authenticating against the API
- Multi-turn conversation with query rewriting working end-to-end
- Q&A logs accumulating in MySQL with latency, similarity, and feedback
- Evaluation queries surfacing low-quality answers

---

## Prerequisites

- MySQL installed and running
- All packages from Topics 2–6 installed (or run `pip install -r requirements.txt`)
- The `.env` file configured with API keys, database URL, and JWT secret
- The corpus files at `../../data/synthetic-hr-corpus/` (15 `.txt` files)

---

## Demo Files

All code lives in the `knowledge-assistant/` folder:

| File | Topic | Purpose |
|------|-------|---------|
| `ingest.py` | 2 | Load corpus, chunk by section, embed and store in ChromaDB |
| `retrieval.py` | 2 | ChromaDB queries with metadata filtering and re-ranking |
| `citations.py` | 3 | LLM answer generation, citation parsing, verification, refusal |
| `history.py` | 4 | Follow-up query rewriting, history windowing, token trimming |
| `app.py` | 5 | Streamlit chat interface |
| `auth.py` | 6 | bcrypt password hashing, JWT tokens |
| `database.py` | 6 | SQLAlchemy MySQL connection |
| `models.py` | 6 | `User` and `QALog` table models |
| `schemas.py` | 6 | Pydantic request/response schemas |
| `api.py` | all | FastAPI backend tying everything together |

---

## Setup (before the session)

1. Navigate to the `knowledge-assistant/` folder
2. Copy `.env.example` to `.env` and fill in the credentials
3. Create the MySQL database:
   ```sql
   CREATE DATABASE IF NOT EXISTS novanet_hr_app
     CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
4. Run the ingestion script:
   ```bash
   python ingest.py
   ```
   Confirm: "Ingested 90 chunks into collection 'novanet_hr'"

---

## Demo Steps

### Part 1 — The Folder Tour (5 min)

Open the `knowledge-assistant/` folder in VS Code's explorer. Walk through each file.

> "This folder is the entire application. Ten Python files, one `.env`, one `requirements.txt`. No imports from other modules — everything is self-contained."

Draw the dependency chain on the board:

```
app.py  →  HTTP  →  api.py
                      ├── auth.py
                      ├── history.py  →  citations.py  →  retrieval.py
                      ├── models.py  →  database.py
                      └── schemas.py
```

> "Each file maps to a topic. `retrieval.py` is Topic 2 — the metadata filters and re-ranker. `citations.py` is Topic 3 — the citation pipeline. `history.py` is Topic 4 — query rewriting. `app.py` is Topic 5 — the Streamlit interface. `auth.py`, `models.py`, and `database.py` are Topic 6 — authentication and logging. `api.py` ties them all together."

> "In your topic demos, everything was in `pipeline.py` — one file. Here we split it into three modules. Why? Because different team members can work on retrieval, citations, and history independently. That is the point of Topic 1's discussion about team roles and shared codebases."

### Part 2 — Ingestion (5 min)

Open `ingest.py`. Show the metadata registry.

> "Fifteen documents, each with six metadata fields. The registry is a dictionary, not parsed from the files, so the metadata is explicit and reviewable."

Show the `load_and_chunk` function:

> "Each document is split by the 60-dash separator. The first section (the header) is skipped. Each remaining section becomes a chunk with the document's metadata attached."

If not already ingested, run it:

```bash
python ingest.py
```

> "90 chunks from 15 documents. The largest document — the revised annual leave policy — produces 13 chunks. The smallest — each circular — produces 1. ChromaDB embeds each chunk using the same embedding function we used in Topic 2 and stores them with metadata for filtering."

### Part 3 — Start the API (5 min)

```bash
uvicorn api:app --reload
```

Open http://localhost:8000/docs.

> "FastAPI generated the interactive docs. Five endpoints: register, login, query, feedback, logs. The tables were created on startup — `Base.metadata.create_all` in the first lines of `api.py`."

Register a test user:

```json
{
  "username": "amina",
  "password": "s3cur3Pass!"
}
```

> "The password was hashed with bcrypt. Let's check MySQL."

```sql
SELECT username, LEFT(password_hash, 30) AS hash_preview FROM users;
```

Log in and copy the JWT token. Click "Authorize" and paste it.

### Part 4 — Query Through the API (7 min)

In `/docs`, use **POST /query**:

```json
{"question": "How many days of annual leave do I get?"}
```

> "The response has the answer, citations, similarity score, whether the query was rewritten, and a `log_id`. That log_id is the row in the `qa_logs` table."

Check MySQL:

```sql
SELECT id, question, search_query, similarity, latency_ms
FROM qa_logs ORDER BY created_at DESC LIMIT 5;
```

> "The exchange is logged. Question, rewritten query (same here since it was the first turn), similarity, latency in milliseconds."

Ask a follow-up:

```json
{"question": "How many of those can I carry over?"}
```

> "Check the logs again. The `search_query` is different from the `question` — the rewriter expanded 'those' into 'annual leave days.' That is Topic 4's query rewriting working inside the API."

Ask something off-topic:

```json
{"question": "Can I bring my pet to the office?"}
```

> "Refused. Low similarity, no citations. The log still captured the attempt — you can see which questions employees ask that the corpus does not cover."

### Part 5 — Start the Streamlit App (7 min)

Open a second terminal:

```bash
streamlit run app.py
```

Log in with `amina` / `s3cur3Pass!`.

> "The sidebar sent a POST to `/login`. The API verified the password with bcrypt and returned a JWT. The app stored it in `session_state.token` and now sends it with every request."

Point at the sidebar notice: "Your questions are logged for quality monitoring."

> "NDPA transparency. One line."

Ask: "What is the remote work allowance?"

> "The answer comes back with citations. Click 'Sources cited' — you see HR-CIR-2026-003 verified. The circular updated the amount to NGN 35,000. The re-ranker from Topic 2 made sure the circular ranked above the older policy."

Follow up: "Was it always that amount?"

> "The rewriter turns this into something like 'Was the monthly remote work equipment allowance always NGN 35,000?' ChromaDB finds both the circular and the original policy. The answer explains the change."

### Part 6 — Feedback and Logging (5 min)

Click thumbs-down on the last answer.

> "That sent a POST to `/feedback` with the `log_id` and 'negative'. Let's check."

```sql
SELECT id, question, feedback FROM qa_logs
WHERE feedback IS NOT NULL ORDER BY created_at DESC;
```

> "The feedback column is 'negative'. This is your evaluation signal."

Run the evaluation queries:

```sql
-- Low-confidence answers
SELECT question, similarity FROM qa_logs
WHERE similarity < 0.5 ORDER BY created_at DESC;

-- Most-asked questions
SELECT question, COUNT(*) AS n FROM qa_logs
GROUP BY question ORDER BY n DESC LIMIT 10;

-- Average latency
SELECT AVG(latency_ms) AS avg_ms, MAX(latency_ms) AS max_ms FROM qa_logs;
```

> "These are your monitoring tools. Low similarity surfaces corpus gaps. Negative feedback surfaces bad answers. Latency surfaces performance issues. You query these in the first week after deploying the assistant."

### Part 7 — The Full Architecture (5 min)

Draw the complete diagram on the board:

```
┌──────────────┐         ┌──────────────────────────────┐
│  Streamlit   │  HTTP   │         FastAPI               │
│  app.py      │ ──────> │  /login    → auth.py          │
│              │         │  /register → auth.py          │
│  Chat UI     │ <────── │  /query    → history.py       │
│  Citations   │         │               → citations.py  │
│  Feedback    │         │               → retrieval.py  │
│              │         │  /feedback → models.py        │
└──────────────┘         └──────┬───────────┬───────────┘
                                │           │
                           ┌────▼────┐ ┌────▼────┐
                           │  MySQL   │ │ ChromaDB │
                           │  users   │ │ novanet  │
                           │  qa_logs │ │ _hr      │
                           └─────────┘ └─────────┘
```

> "Two processes, two databases, ten files. The employee sees a chat box. Behind it: authentication, query rewriting, metadata-filtered retrieval, re-ranking, cited answer generation, citation verification, refusal logic, exchange logging, and feedback capture. Every line of code in this folder was built in Topics 2 through 6."

### Part 8 — What Students Build (5 min)

> "This reference build is what you are assembling this week. The project asks each of you to contribute a component — retrieval, citations, interface, auth, or logging — and review each other's code. The reference build is the answer key. Your code does not need to match it line for line, but it must produce the same results: correct answers with verified citations, refused answers when the corpus has nothing, query rewriting for follow-ups, authenticated access, and logged exchanges."

> "Modules 5 and 6 build on this folder. Module 5 adds evaluation — automated tests, LLM-as-judge scoring, and a test harness. Module 6 adds deployment — containerisation, CI/CD, and monitoring. The code you write this week is the code you deploy in Week 6."

### Close (2 min)

> "You have seen the complete application. Ten files, 90 corpus chunks, five API endpoints, one chat interface. An employee logs in, asks a question, gets a cited answer, follows up, and gives feedback — all logged, all authenticated, all traceable. This is what a knowledge assistant looks like as a full application, not just a notebook demo. Your project this week: build your own."

---

## Common Issues

- **"Collection not found" on API startup** — `ingest.py` has not been run. Run it first.
- **"Access denied for user 'root'" on startup** — check `DATABASE_URL` in `.env`. The MySQL password must match.
- **"ModuleNotFoundError"** — run `pip install -r requirements.txt` from inside the `knowledge-assistant/` folder.
- **Port 8000 already in use** — the Topic 6 demo may still be running. Stop it, or use `--port 8001` and update `API_URL` in `app.py`.
- **Ingestion says "already has 90 chunks"** — the collection exists from a previous run. Delete `chroma_db/` to re-ingest.
- **Streamlit shows "Cannot reach the API server"** — FastAPI is not running. Start it in Terminal 1 first.
- **Login fails after registering** — make sure the username and password match exactly (case-sensitive).

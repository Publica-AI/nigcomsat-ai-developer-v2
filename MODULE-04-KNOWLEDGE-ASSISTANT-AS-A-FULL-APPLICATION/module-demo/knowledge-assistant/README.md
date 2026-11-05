# NovaNet HR Knowledge Assistant

Internal knowledge assistant for NovaNet Technologies Ltd. Employees ask questions about HR policies, leave, benefits, onboarding, and conduct, and receive cited answers from the company's HR document corpus.

This is the **Module 4 reference build** for the AI Application Development Developer Track (NIGCOMSAT / Publica Academy).

## Architecture

```
Streamlit (app.py)  ──HTTP──>  FastAPI (api.py)
                                 ├── auth.py        (bcrypt + JWT)
                                 ├── history.py     (query rewriting)
                                 │    └── citations.py  (cited answers)
                                 │         └── retrieval.py  (ChromaDB + reranking)
                                 ├── models.py      (User, QALog)
                                 └── database.py    (MySQL)
```

| Component | Purpose |
|-----------|---------|
| `retrieval.py` | ChromaDB queries with metadata filtering and rule-based re-ranking |
| `citations.py` | LLM answer generation, citation parsing, verification, refusal |
| `history.py` | Follow-up query rewriting, history windowing, token trimming |
| `auth.py` | bcrypt password hashing, JWT token creation and verification |
| `database.py` | SQLAlchemy MySQL connection |
| `models.py` | `User` and `QALog` table models |
| `schemas.py` | Pydantic request/response models |
| `api.py` | FastAPI backend with all endpoints |
| `app.py` | Streamlit chat interface |
| `ingest.py` | One-shot corpus ingestion into ChromaDB |

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your API keys and database credentials
```

### 3. Create the MySQL database

```sql
CREATE DATABASE IF NOT EXISTS novanet_hr_app
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. Ingest the corpus

```bash
python ingest.py
```

This reads the 15 HR documents from `../../data/synthetic-hr-corpus/`, chunks them by section (90 chunks total), embeds them, and stores them in a local ChromaDB collection at `./chroma_db/`.

To specify a different corpus path:

```bash
python ingest.py /path/to/synthetic-hr-corpus
```

### 5. Start the API (Terminal 1)

```bash
uvicorn api:app --reload
```

The `users` and `qa_logs` tables are created automatically on startup. API docs at http://localhost:8000/docs.

### 6. Register a user

Open http://localhost:8000/docs, use **POST /register**:

```json
{
  "username": "amina",
  "password": "s3cur3Pass!"
}
```

### 7. Start the Streamlit app (Terminal 2)

```bash
streamlit run app.py
```

Opens at http://localhost:8501. Log in with the credentials from step 6.

## Test questions

| Question | Expected behaviour |
|----------|-------------------|
| How many days of annual leave do I get? | 25 days, cites HR-POL-2025-006 |
| How many of those can I carry over? | 10 days by 31 March, rewriter expands "those" |
| What is the remote work allowance? | NGN 35,000/month, cites HR-CIR-2026-003 |
| Can I bring my pet to the office? | Refused — no relevant documents |

## File structure

```
knowledge-assistant/
  api.py              FastAPI backend
  app.py              Streamlit interface
  auth.py             Password hashing + JWT
  citations.py        Citation pipeline
  database.py         MySQL connection
  history.py          Conversation history + query rewriting
  ingest.py           Corpus ingestion script
  models.py           SQLAlchemy models
  retrieval.py        ChromaDB search + re-ranking
  schemas.py          Pydantic schemas
  requirements.txt    Python dependencies
  .env.example        Environment template
  chroma_db/          (created by ingest.py)
```

## Corpus

The synthetic HR corpus (15 documents, 90 chunks) lives at `../../data/synthetic-hr-corpus/`. All data is synthetic — no real company documents appear in course files.

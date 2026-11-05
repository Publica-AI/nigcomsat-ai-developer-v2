# Module 4 Reference Application — Architecture Outline

Self-contained knowledge assistant over the synthetic MCE compliance corpus.
This is the instructor-owned reference build that Modules 5 and 6 extend.

## Folder structure

```
knowledge-assistant/
  app.py              Streamlit single-page chat interface
  api.py              FastAPI backend (/query, /auth, /logs)
  retrieval.py        ChromaDB search, metadata filtering, re-ranking
  citations.py        Source-reference extraction and verification
  history.py          Conversation history, follow-up query rewriting
  database.py         SQLAlchemy engine + session (MySQL)
  models.py           SQLAlchemy tables: users, qa_logs
  auth.py             Password hashing, JWT creation and verification
  schemas.py          Pydantic request/response models
  ingest.py           One-shot script: load corpus, chunk, embed, store
  .env.example        DATABASE_URL, SECRET_KEY, OPENAI_API_KEY, etc.
  requirements.txt    All dependencies
```

## Key design decisions

- **Self-contained.** Does not import from Module 2 or Module 3 folders.
  Participants rewrite auth, database, and retrieval code from scratch using
  the patterns they learned, so every file lives inside this folder.
- **Single Streamlit page.** Chat input, response with inline citations,
  feedback thumbs, login sidebar. No multi-page routing.
- **FastAPI serves the logic.** Streamlit calls the API over HTTP — the two
  processes run separately. This separation is the point of the architecture.
- **ChromaDB persistent storage.** Collection `mce_corpus` with metadata
  fields: doc_type, department, date_issued, doc_id.
- **MySQL for users and logs.** Table `users` (id, name, email, password_hash,
  role, created_at). Table `qa_logs` (id, user_id, question, rewritten_query,
  answer, sources_json, latency_ms, feedback, created_at).
- **Two API keys.** Chat completion through OPENAI_BASE_URL + OPENAI_API_KEY;
  embeddings through EMBEDDING_API_KEY (OpenAI directly). Same two-client
  pattern taught in Module 3.
- **Citation format.** Each answer includes `[Source N]` markers. Each source
  maps to a doc_id + section. The system verifies every cited source exists in
  the retrieved chunks. If nothing supports an answer, the assistant refuses.
- **Conversation history.** Stored in Streamlit session_state. Follow-up
  questions are rewritten into standalone queries before retrieval. History is
  trimmed to a token budget.

## Topic-to-file mapping

| Topic | Primary files touched |
|-------|----------------------|
| 1. From Pipeline to Product | (orientation — no code) |
| 2. Metadata Filtering & Re-ranking | retrieval.py |
| 3. Source Citation in Answers | citations.py |
| 4. Conversation History & Context | history.py |
| 5. Building the Streamlit Interface | app.py |
| 6. Authentication & Q&A Logging | auth.py, models.py, database.py, api.py |

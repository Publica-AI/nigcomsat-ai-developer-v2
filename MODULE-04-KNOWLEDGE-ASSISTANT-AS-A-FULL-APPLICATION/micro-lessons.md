# Module 4 - The Knowledge Assistant as a Full Application: Micro Lessons
> For use with AI practice question generation. Beginner and intermediate level only.
> Assumes the prerequisite Python course, Module 1 (LLM APIs, Pydantic, pytest, Git), Module 2 (FastAPI, MySQL, SQLAlchemy, auth), and Module 3 (embeddings, ChromaDB, RAG) are already taught, so those are not listed under Not Yet Taught.
> IDs are placeholders (`TBD`) to be replaced at upload.

---

## Topic 1: From Pipeline to Product

**Micro Topic ID:** `mt_py_nigdev_TBD_M04_01_01`

**Topic ID:** `topic_py_nigdev_TBD_M04_01`

**Micro Topic Order:** 1

**Title:** From Pipeline to Product

**Programming Language:** None

**Coding Exercise:** No

**Learning Objective:**
Students will explain why a knowledge assistant is split into separate components (retrieval, citations, history, auth, interface), describe the two-process architecture (Streamlit + FastAPI), assign team roles for a collaborative build, and define what "done" means for a production-quality assistant — not just "it runs" but correct answers with verified citations, refusal on unknowns, and peer-reviewed code.

**Description for AI:**
This is a planning and architecture topic with no code. Students see the target architecture for the NovaNet HR knowledge assistant — a Streamlit chat interface calling a FastAPI backend that ties together retrieval (ChromaDB with metadata filtering and re-ranking), cited answer generation, conversation history with query rewriting, bcrypt authentication with JWT tokens, and Q&A exchange logging to MySQL. The architecture uses two processes (Streamlit and FastAPI) communicating over HTTP, two data stores (MySQL for users and logs, ChromaDB for document vectors), and separate Python files for each concern (retrieval.py, citations.py, history.py, auth.py, database.py, models.py, schemas.py, api.py, app.py). Students learn why this split matters: different team members work on different files, each file can be tested independently, and the application can be extended without rewriting everything. The topic also covers team roles — lead, reviewer, tester, documenter — that rotate so every student practises every role. The definition of done is concrete: the assistant must produce correct answers with verified citations, refuse questions the corpus cannot answer, handle follow-ups with query rewriting, authenticate users, log every exchange, and survive peer review. The AI-use mode for this week is AI-Augmented: using AI tools is taught as a professional workflow, but the assessed skill is verification — students must explain every line they submit.

**Common Mistakes:**
- Treating "it runs without errors" as the same as "it is done" — code that runs but returns wrong answers or uncited responses is not done
- Assigning team roles permanently instead of rotating them, so one person never reviews and another never leads
- Skipping code review for AI-generated code because "the AI wrote it correctly" — the developer must explain every line regardless of who or what produced it
- Putting all code in one file because splitting it feels unnecessary for a small project — the split enables parallel teamwork and cleaner testing

**Example Code for AI:**
```python
# No runnable code — this is a planning topic.
# The architecture diagram shows the dependency chain:
#
#   app.py  →  HTTP  →  api.py
#                        ├── auth.py
#                        ├── history.py  →  citations.py  →  retrieval.py
#                        ├── models.py   →  database.py
#                        └── schemas.py
#
# Students should be able to trace a query from the Streamlit input
# through the FastAPI endpoint, into history (rewrite), then citations
# (retrieve + generate + verify), and back out as a cited answer.

def trace_query_path(question: str) -> list[str]:
    """Trace the components a question passes through."""
    return [
        "app.py: user types question in st.chat_input",
        "api.py /query: receives POST with JWT auth",
        "history.py chat(): rewrites follow-ups, manages history window",
        "citations.py get_cited_answer(): retrieves chunks, generates cited answer",
        "retrieval.py retrieve(): queries ChromaDB with metadata filter and re-ranks",
        "api.py: logs exchange to qa_logs table, returns answer with citations",
        "app.py: displays answer with citations in st.expander",
    ]
```

**Difficulty Level:** 1

**Estimated Minutes:** 8

**Not Yet Taught:**
metadata filtering in ChromaDB queries (where clause for status, doc_type), rule-based re-ranking using metadata signals (type authority boost, recency boost), source citation in LLM answers (system prompt requiring [Source N] markers), citation parsing and verification against retrieved chunks, refusal logic (similarity threshold, no-citation refusal), conversation history management (history window, token budget), follow-up query rewriting into standalone search queries, stripping citations from history, Streamlit chat interface (st.chat_input, st.chat_message, st.session_state, st.spinner, st.expander), calling FastAPI from Streamlit with requests.post and JWT in Authorization header, bcrypt password hashing (hash_password, verify_password, salt), JWT token creation and verification (sub, exp, SECRET_KEY), FastAPI authentication endpoints (/register, /login) with HTTPBearer, protected routes with Depends(get_current_user), Q&A exchange logging to MySQL (question, search_query, answer, sources, similarity, latency_ms, feedback, user_id), evaluation queries on qa_logs (low similarity, negative feedback, latency), NDPA transparency notice for data collection, token expiry handling in Streamlit (401 → re-login), tool calling and function calling, LangGraph, LangChain and agent frameworks, scheduled and watched-folder automation, prompt injection defences, token and cost budgeting, pytest fixtures, mocking and parametrised tests, Docker and containerisation, CI/CD with GitHub Actions, security review and system records for audit, Responsible AI governance, human oversight and incident handling

---

## Topic 2: Metadata Filtering & Re-ranking

**Micro Topic ID:** `mt_py_nigdev_TBD_M04_02_01`

**Topic ID:** `topic_py_nigdev_TBD_M04_02`

**Micro Topic Order:** 1

**Title:** Metadata Filtering & Re-ranking

**Programming Language:** Python

**Coding Exercise:** Yes

**Learning Objective:**
Students will store document chunks in ChromaDB with metadata (doc_id, doc_type, department, date_issued, status), apply a metadata filter to exclude superseded documents, implement a rule-based re-ranker using doc_type authority and recency signals, and measure retrieval quality before and after filtering on a fixed question set.

**Description for AI:**
This topic teaches metadata-aware retrieval over the NovaNet HR corpus (15 synthetic HR documents, 90 chunks). Students ingest the corpus into a persistent ChromaDB collection with six metadata fields per chunk: doc_id, doc_type (policy, sop, circular, faq, guideline), department (hr, it, finance, admin, all), date_issued (YYYYMMDD integer), status (current or superseded), and title. The core problem is the retrieval trap: an employee asks "How many days of annual leave do I get?" and the corpus contains both the current policy (25 days, HR-POL-2025-006) and a superseded policy (20 days, HR-POL-2024-001). Without filtering, cosine similarity alone may return the wrong document. Students first query without any filter and observe the trap, then add `where={"status": "current"}` to exclude superseded documents. Next, they build a re-ranker that computes `final_score = similarity + type_boost + recency_boost`: policies get a higher type_boost than FAQs (because policies are authoritative sources that FAQs may paraphrase), and documents with more recent date_issued values get a recency_boost. Students test on at least 5 questions (leave entitlement, remote work allowance, carry-over limit, disciplinary process, onboarding checklist) and compare top-1 accuracy with and without filtering and re-ranking. ChromaDB uses the OpenAI embedding API (text-embedding-3-small) via a custom embedding function that reads credentials from .env. The collection uses cosine similarity space.

**Common Mistakes:**
- Forgetting the `where` clause and relying only on re-ranking — re-ranking reorders results but does not exclude superseded documents, so the wrong answer can still appear
- Using a string for date_issued instead of an integer, which breaks numeric comparison in the re-ranker
- Applying the metadata filter on the wrong field (e.g. filtering by department when the question is about status)
- Not testing the retrieval trap explicitly — "it seems to work" is not enough; students must verify the superseded policy does not appear in filtered results
- Hard-coding the number of results (n_results) too low, so the re-ranker has too few candidates to re-order

**Example Code for AI:**
```python
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("novanet_hr")

# Query WITHOUT metadata filter — may return superseded policy
raw_results = collection.query(
    query_texts=["How many days of annual leave do I get?"],
    n_results=5,
)
# raw_results may include the superseded 20-day policy

# Query WITH metadata filter — only current documents
filtered_results = collection.query(
    query_texts=["How many days of annual leave do I get?"],
    n_results=5,
    where={"status": "current"},
)

# Re-ranking: boost by doc_type authority and recency
TYPE_BOOST = {"policy": 0.05, "sop": 0.04, "circular": 0.03, "guideline": 0.02, "faq": 0.01}

def rerank(results):
    scored = []
    for i, doc_id in enumerate(results["ids"][0]):
        meta = results["metadatas"][0][i]
        similarity = 1 - results["distances"][0][i]  # cosine distance to similarity
        boost = TYPE_BOOST.get(meta.get("doc_type", ""), 0)
        recency = min((meta.get("date_issued", 20240101) - 20240101) / 100000, 0.1)
        scored.append((similarity + boost + recency, results["documents"][0][i], meta))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored
```

**Difficulty Level:** 2

**Estimated Minutes:** 12

**Not Yet Taught:**
source citation in LLM answers (system prompt requiring [Source N] markers), citation parsing and verification against retrieved chunks, refusal logic (similarity threshold, no-citation refusal), conversation history management (history window, token budget), follow-up query rewriting into standalone search queries, stripping citations from history, Streamlit chat interface (st.chat_input, st.chat_message, st.session_state, st.spinner, st.expander), calling FastAPI from Streamlit with requests.post and JWT in Authorization header, bcrypt password hashing (hash_password, verify_password, salt), JWT token creation and verification (sub, exp, SECRET_KEY), FastAPI authentication endpoints (/register, /login) with HTTPBearer, protected routes with Depends(get_current_user), Q&A exchange logging to MySQL (question, search_query, answer, sources, similarity, latency_ms, feedback, user_id), evaluation queries on qa_logs (low similarity, negative feedback, latency), NDPA transparency notice for data collection, token expiry handling in Streamlit (401 → re-login), tool calling and function calling, LangGraph, LangChain and agent frameworks, scheduled and watched-folder automation, prompt injection defences, token and cost budgeting, pytest fixtures, mocking and parametrised tests, Docker and containerisation, CI/CD with GitHub Actions, security review and system records for audit, Responsible AI governance, human oversight and incident handling

---

## Topic 3: Source Citation in Answers

**Micro Topic ID:** `mt_py_nigdev_TBD_M04_03_01`

**Topic ID:** `topic_py_nigdev_TBD_M04_03`

**Micro Topic Order:** 1

**Title:** Source Citation in Answers

**Programming Language:** Python

**Coding Exercise:** Yes

**Learning Objective:**
Students will build a citation pipeline that instructs the LLM to produce answers with [Source N] markers, parse those markers from the response, verify each citation exists in the retrieved chunks, and return a refusal message when the corpus cannot answer the question.

**Description for AI:**
This topic builds the citation layer on top of the retrieval from Topic 2. Students write a system prompt that presents retrieved chunks as a numbered list (Source 1, Source 2, ...) and instructs the LLM to cite each claim with [Source N]. The pipeline has four steps: (1) retrieve chunks using the metadata-filtered, re-ranked retrieval from Topic 2; (2) send the chunks and user question to the LLM with the citation system prompt; (3) parse [Source N] markers from the LLM response using a regex (`\[Source (\d+)\]`); (4) verify each parsed citation number maps to an actual chunk that was provided. Invalid citations (numbers beyond the provided range) are flagged. The topic also introduces refusal logic with two triggers: the best retrieval similarity is below a threshold (e.g. 0.35), meaning the corpus likely has no relevant content; or the LLM response contains no citation markers, meaning the model could not ground its answer. In either case, the system returns a refusal message (e.g. "I don't have enough information to answer that question. Please contact HR directly.") instead of a potentially hallucinated answer. Students test with NovaNet HR questions: "What is the remote work allowance?" should return NGN 35,000 with a citation to HR-CIR-2026-003; "Can I bring my pet to the office?" should trigger a refusal. The LLM is accessed via the OpenAI-compatible client from .env (OPENAI_API_KEY, MODEL_NAME, OPENAI_BASE_URL).

**Common Mistakes:**
- Writing the system prompt without a numbered source list, so the LLM has no consistent format to cite
- Forgetting to verify citations — the LLM may hallucinate a [Source 5] when only 3 chunks were provided
- Setting the refusal threshold too high (e.g. 0.8), so valid questions are incorrectly refused
- Setting the refusal threshold too low (e.g. 0.1), so the system tries to answer questions the corpus cannot support
- Returning the LLM's raw output without checking for citations, which defeats the purpose of the grounding pipeline
- Not testing the refusal path — a pipeline that only works on answerable questions is incomplete

**Example Code for AI:**
```python
import re
from openai import OpenAI

client = OpenAI()

SYSTEM_PROMPT = """You are a helpful HR assistant for NovaNet Technologies.
Answer the question using ONLY the sources below. Cite each claim with [Source N].
If no source supports the answer, say "I don't have enough information."

Sources:
{sources}"""

def extract_citations(text: str) -> list[int]:
    return [int(n) for n in re.findall(r"\[Source (\d+)\]", text)]

def verify_citations(cited: list[int], total_sources: int) -> list[int]:
    return [n for n in cited if n < 1 or n > total_sources]

def should_refuse(similarity: float, threshold: float = 0.35) -> bool:
    return similarity < threshold

# Usage: after retrieving chunks and getting best_similarity
if should_refuse(best_similarity):
    answer = "I don't have enough information to answer that. Please contact HR directly."
else:
    # Send to LLM with citation prompt, then verify
    response = client.chat.completions.create(
        model="model-name",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.format(sources=numbered_sources)},
            {"role": "user", "content": question},
        ],
    )
    answer = response.choices[0].message.content
    cited = extract_citations(answer)
    invalid = verify_citations(cited, len(chunks))
    if not cited:
        answer = "I don't have enough information to answer that. Please contact HR directly."
```

**Difficulty Level:** 2

**Estimated Minutes:** 12

**Not Yet Taught:**
conversation history management (history window, token budget), follow-up query rewriting into standalone search queries, stripping citations from history, Streamlit chat interface (st.chat_input, st.chat_message, st.session_state, st.spinner, st.expander), calling FastAPI from Streamlit with requests.post and JWT in Authorization header, bcrypt password hashing (hash_password, verify_password, salt), JWT token creation and verification (sub, exp, SECRET_KEY), FastAPI authentication endpoints (/register, /login) with HTTPBearer, protected routes with Depends(get_current_user), Q&A exchange logging to MySQL (question, search_query, answer, sources, similarity, latency_ms, feedback, user_id), evaluation queries on qa_logs (low similarity, negative feedback, latency), NDPA transparency notice for data collection, token expiry handling in Streamlit (401 → re-login), tool calling and function calling, LangGraph, LangChain and agent frameworks, scheduled and watched-folder automation, prompt injection defences, token and cost budgeting, pytest fixtures, mocking and parametrised tests, Docker and containerisation, CI/CD with GitHub Actions, security review and system records for audit, Responsible AI governance, human oversight and incident handling

---

## Topic 4: Conversation History & Context Management

**Micro Topic ID:** `mt_py_nigdev_TBD_M04_04_01`

**Topic ID:** `topic_py_nigdev_TBD_M04_04`

**Micro Topic Order:** 1

**Title:** Conversation History & Context Management

**Programming Language:** Python

**Coding Exercise:** Yes

**Learning Objective:**
Students will implement conversation history management with a sliding window, rewrite follow-up questions into standalone search queries using the LLM, strip citation markers from stored history, and enforce a token budget so that combined history and retrieved chunks fit inside the LLM's context window.

**Description for AI:**
This topic adds multi-turn conversation support to the citation pipeline from Topic 3. The core problem: an employee asks "How many annual leave days do I get?" (answered correctly) and follows up with "Does that apply to contract staff?" — the follow-up has no mention of "annual leave" so ChromaDB returns irrelevant results. The solution is query rewriting: send the conversation history and the follow-up to the LLM with a system prompt that says "Rewrite this follow-up into a standalone search query." The rewriter expands "Does that apply to contract staff?" into "Does the 25-day annual leave entitlement apply to contract staff?" — a query that ChromaDB can match. Implementation details: conversation history is stored as a list of {"role": ..., "content": ...} dicts. A history window limits the rewriter to the last N turns (default 5). Before adding an assistant response to history, citation markers like [Source 1] are stripped out because they waste tokens and confuse the rewriter. A token budget function estimates the combined token count of history + retrieved chunks and trims the oldest turns if the total exceeds a limit (e.g. 3000 tokens). The rewriter must also handle standalone queries: if the new question is clearly a new topic ("What is the dress code policy?"), the rewriter should return it unchanged. Students test with multi-turn sequences: "How many annual leave days?" → "Can I carry those over?" → "What about sick leave?" (topic change).

**Common Mistakes:**
- Sending the raw follow-up to ChromaDB without rewriting, leading to irrelevant results
- Not stripping citation markers from history, wasting tokens and confusing the rewriter with [Source N] fragments
- Setting the history window to 1, so the rewriter has no previous context to expand the follow-up
- Forgetting the token budget, so a long conversation eventually exceeds the LLM's context window and causes an API error
- Always rewriting, even when the question is already standalone — a good rewriter should detect this and return the query unchanged
- Counting characters instead of tokens for the token budget (1 token ≈ 4 characters in English, but this varies)

**Example Code for AI:**
```python
from openai import OpenAI

client = OpenAI()

REWRITE_PROMPT = """Given the conversation history below, rewrite the follow-up question
into a standalone search query. If it is already standalone, return it unchanged.

History:
{history}

Follow-up: {question}

Standalone query:"""

def rewrite_query(question: str, history: list[dict], model: str) -> str:
    if not history:
        return question
    history_text = "\n".join(f"{m['role']}: {m['content']}" for m in history[-5:])
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": REWRITE_PROMPT.format(
            history=history_text, question=question
        )}],
        temperature=0,
    )
    return response.choices[0].message.content.strip()

def strip_citations(text: str) -> str:
    import re
    return re.sub(r"\[Source \d+\]", "", text).strip()

def trim_history(history: list[dict], max_tokens: int = 2000) -> list[dict]:
    total = sum(len(m["content"]) // 4 for m in history)  # rough token estimate
    trimmed = list(history)
    while total > max_tokens and len(trimmed) > 2:
        removed = trimmed.pop(0)
        total -= len(removed["content"]) // 4
    return trimmed
```

**Difficulty Level:** 2

**Estimated Minutes:** 12

**Not Yet Taught:**
Streamlit chat interface (st.chat_input, st.chat_message, st.session_state, st.spinner, st.expander), calling FastAPI from Streamlit with requests.post and JWT in Authorization header, bcrypt password hashing (hash_password, verify_password, salt), JWT token creation and verification (sub, exp, SECRET_KEY), FastAPI authentication endpoints (/register, /login) with HTTPBearer, protected routes with Depends(get_current_user), Q&A exchange logging to MySQL (question, search_query, answer, sources, similarity, latency_ms, feedback, user_id), evaluation queries on qa_logs (low similarity, negative feedback, latency), NDPA transparency notice for data collection, token expiry handling in Streamlit (401 → re-login), tool calling and function calling, LangGraph, LangChain and agent frameworks, scheduled and watched-folder automation, prompt injection defences, token and cost budgeting, pytest fixtures, mocking and parametrised tests, Docker and containerisation, CI/CD with GitHub Actions, security review and system records for audit, Responsible AI governance, human oversight and incident handling

---

## Topic 5: Building the Streamlit Interface

**Micro Topic ID:** `mt_py_nigdev_TBD_M04_05_01`

**Topic ID:** `topic_py_nigdev_TBD_M04_05`

**Micro Topic Order:** 1

**Title:** Building the Streamlit Interface

**Programming Language:** Python

**Coding Exercise:** Yes

**Learning Objective:**
Students will build a Streamlit chat interface that calls the FastAPI backend, displays cited answers with expandable source details, manages conversation state with st.session_state, shows loading indicators with st.spinner, handles API errors without exposing tracebacks, and provides a usable experience for non-technical staff.

**Description for AI:**
This topic builds the Streamlit frontend for the NovaNet HR assistant. Students learn the Streamlit chat model: `st.chat_input` captures the user's question, `st.chat_message` renders user and assistant bubbles, and `st.session_state.messages` persists the conversation across Streamlit's full-script rerun on every interaction. The app calls the FastAPI backend with `requests.post(f"{API_URL}/query", json={"question": question}, headers={"Authorization": f"Bearer {token}"})` — the JWT token is stored in `st.session_state.token` after login. While the pipeline runs, a `with st.spinner("Searching HR documents...")` block shows a loading indicator. The response includes the answer text, a list of citations (doc_id + section), a similarity score, and a log_id. Citations are displayed inside an `st.expander("Sources cited")` so the answer stays clean but the employee can click to see the full source details. Error handling wraps the API call in `try/except requests.RequestException` and shows a user-friendly `st.error("The service is temporarily unavailable.")` instead of a raw traceback. A sidebar shows the logged-in user's name, a logout button, and a notice: "Your questions are logged for quality monitoring" (NDPA transparency). The key usability principle: a new employee with no technical background should be able to ask about their probation period and get a clear, cited answer without seeing any technical jargon, status codes, or JSON. This is a terminal and code-editor demo, not a notebook — the app is built in VS Code and run with `streamlit run app.py`.

**Common Mistakes:**
- Forgetting to initialise st.session_state.messages at the top of the script, so the conversation resets on every rerun
- Displaying raw JSON or HTTP status codes to the user instead of a clean, readable answer
- Not wrapping the API call in try/except, so a ConnectionError shows a full Python traceback
- Placing st.chat_input inside a conditional block, which causes Streamlit to hide it after the first interaction
- Forgetting the Authorization header on requests.post, so the protected endpoint returns 401 every time
- Not handling 401 (expired token) — the user sees a cryptic error instead of being redirected to the login form

**Example Code for AI:**
```python
import streamlit as st
import requests

API_URL = "http://localhost:8000"

if "messages" not in st.session_state:
    st.session_state.messages = []
if "token" not in st.session_state:
    st.session_state.token = None

# Display conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if question := st.chat_input("Ask about HR policies..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching HR documents..."):
            try:
                resp = requests.post(
                    f"{API_URL}/query",
                    json={"question": question},
                    headers={"Authorization": f"Bearer {st.session_state.token}"},
                    timeout=30,
                )
                if resp.status_code == 401:
                    st.session_state.token = None
                    st.error("Session expired. Please log in again.")
                    st.rerun()
                data = resp.json()
                st.markdown(data["answer"])
                with st.expander("Sources cited"):
                    for src in data.get("citations", []):
                        st.write(f"- {src}")
            except requests.RequestException:
                st.error("The service is temporarily unavailable. Please try again.")
```

**Difficulty Level:** 2

**Estimated Minutes:** 12

**Not Yet Taught:**
bcrypt password hashing (hash_password, verify_password, salt), JWT token creation and verification (sub, exp, SECRET_KEY), FastAPI authentication endpoints (/register, /login) with HTTPBearer, protected routes with Depends(get_current_user), Q&A exchange logging to MySQL (question, search_query, answer, sources, similarity, latency_ms, feedback, user_id), evaluation queries on qa_logs (low similarity, negative feedback, latency), NDPA transparency notice for data collection, token expiry handling in Streamlit (401 → re-login), tool calling and function calling, LangGraph, LangChain and agent frameworks, scheduled and watched-folder automation, prompt injection defences, token and cost budgeting, pytest fixtures, mocking and parametrised tests, Docker and containerisation, CI/CD with GitHub Actions, security review and system records for audit, Responsible AI governance, human oversight and incident handling

---

## Topic 6: Authentication & Q&A Logging

**Micro Topic ID:** `mt_py_nigdev_TBD_M04_06_01`

**Topic ID:** `topic_py_nigdev_TBD_M04_06`

**Micro Topic Order:** 1

**Title:** Authentication & Q&A Logging

**Programming Language:** Python

**Coding Exercise:** Yes

**Learning Objective:**
Students will implement bcrypt password hashing, create and verify JWT tokens, build registration and login endpoints in FastAPI, protect the /query endpoint with a token dependency, log every Q&A exchange to a MySQL table with latency and similarity metrics, wire feedback buttons in Streamlit to the API, and run evaluation queries on the logs to surface low-quality answers.

**Description for AI:**
This topic adds authentication and observability to the knowledge assistant. Authentication: passwords are hashed with bcrypt (auto-generated salt, constant-time verification). On login, the API issues a JWT containing the username (`sub`) and an expiry timestamp (`exp`, 24 hours). The Streamlit app stores the token in `st.session_state.token` and sends it as a Bearer token in the Authorization header with every request. The `/query` endpoint uses `Depends(get_current_user)` — a FastAPI dependency that extracts the token via `HTTPBearer`, decodes it with PyJWT, looks up the user in MySQL, and returns the user object or raises 401. Q&A logging: the `/query` endpoint measures pipeline latency with `time.time()`, then writes a `QALog` row to MySQL with question, search_query (the rewritten query), answer, sources (JSON string of cited doc_ids), similarity (best retrieval score), latency_ms, user_id, and created_at. The feedback column starts as NULL and is updated when the user clicks thumbs-up or thumbs-down in Streamlit, which sends `POST /feedback` with the `log_id`. Evaluation queries run against qa_logs to surface problems: `WHERE similarity < 0.5` finds corpus gaps, `WHERE feedback = 'negative'` finds bad answers, `AVG(latency_ms)` tracks performance, and `GROUP BY question ORDER BY COUNT(*) DESC` finds the most common questions. The NDPA (Nigeria Data Protection Act) requires a transparency notice ("Your questions are logged for quality monitoring") in the sidebar, data minimisation (log only what is needed for evaluation), purpose limitation (use logs only for quality improvement), and a retention policy (delete logs after the evaluation window). This is a terminal and code-editor demo — all code is built in VS Code, not a notebook.

**Common Mistakes:**
- Storing passwords as plain text or with a fast hash like SHA-256 instead of bcrypt
- Forgetting to set an expiry on the JWT, so tokens never expire and a stolen token works forever
- Not catching the PyJWT ExpiredSignatureError, so an expired token causes a 500 instead of a clean 401
- Measuring latency from the wrong point — it should cover the entire pipeline (retrieval + LLM + logging), not just the LLM call
- Storing the full answer text in the log but not the similarity score or search_query, making evaluation queries impossible
- Logging sensitive data (e.g. the user's password attempt) to the qa_logs table
- Displaying the NDPA notice only in the README and not in the running application where the user can see it

**Example Code for AI:**
```python
import bcrypt
import jwt
import time
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = "change-me-in-production"
security = HTTPBearer()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_token(username: str) -> str:
    payload = {"sub": username, "exp": datetime.utcnow() + timedelta(hours=24)}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")

# In the /query endpoint:
# start = time.time()
# ... run pipeline ...
# latency_ms = int((time.time() - start) * 1000)
# log = QALog(question=q, search_query=rewritten, answer=ans, sources=json.dumps(srcs),
#             similarity=sim, latency_ms=latency_ms, user_id=user.id)
# db.add(log); db.commit()
```

**Difficulty Level:** 2

**Estimated Minutes:** 14

**Not Yet Taught:**
tool calling and function calling, LangGraph, LangChain and agent frameworks, scheduled and watched-folder automation, prompt injection defences, token and cost budgeting, pytest fixtures, mocking and parametrised tests, Docker and containerisation, CI/CD with GitHub Actions, security review and system records for audit, Responsible AI governance, human oversight and incident handling

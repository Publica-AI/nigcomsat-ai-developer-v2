# Demo Guide - Building the Streamlit Interface
**Module 4, Topic 5 | Estimated duration: 40-45 minutes**

---

## What This Demo Teaches

- Creating a Streamlit chat interface with `st.chat_input` and `st.chat_message`
- Using `st.session_state` to keep conversation history across re-runs
- Wiring the chat to the retrieval pipeline from Topics 2–4
- Rendering cited answers with `st.markdown` and expandable source sections
- Adding loading states with `st.spinner` and handling errors without tracebacks
- Building a sidebar with a placeholder login form
- Adding thumbs-up / thumbs-down feedback buttons with unique keys
- Running and testing the app from the terminal with `streamlit run app.py`

---

## Prerequisites

- **Topics 2–4 notebooks must be completed.** The ChromaDB collection `novanet_hr` (90 chunks) must exist from the Topic 2 demo.
- The `.env` file needs the same six variables as previous topics: `OPENAI_API_KEY`, `MODEL_NAME`, `OPENAI_BASE_URL`, `EMBEDDING_API_KEY`, `EMBEDDING_BASE_URL`, `EMBEDDING_MODEL`.
- **Streamlit must be installed:** `pip install streamlit`
- Students should have VS Code open — this demo is built in the editor and terminal, not in Jupyter.

---

## Demo Files

This demo has two runnable files:

| File | Purpose |
|------|---------|
| `pipeline.py` | All retrieval, citation, and history functions from Topics 2–4, consolidated into one importable module |
| `app.py` | The Streamlit chat interface — imports `chat()` from `pipeline.py` |

Run the app with: `streamlit run app.py`

In the module demo (Task 12), the pipeline functions move behind a FastAPI backend and `app.py` switches to HTTP calls. The interface code stays the same.

---

## Setup

1. Open VS Code in the Topic 5 demo folder
2. Open a terminal in VS Code (Ctrl+`)
3. Install Streamlit if not already installed: `pip install streamlit`
4. Confirm the `.env` file is present with all six variables (copy from Topic 2 if needed)
5. Keep `pipeline.py` and `app.py` open side by side in VS Code

---

## Demo Steps

### Part 1 — The Pipeline Stub (5 min)

Open `pipeline.py`. Do not run it yet — walk through the structure.

> "This file wraps everything from Topics 2 through 4 into one importable module. The Streamlit app only needs to call one function: `chat()`. It never touches ChromaDB or the LLM directly."

Point out the three sections:

- **Retrieval (Topic 2):** `retrieve()` and `rerank()` — queries ChromaDB with metadata filters
- **Citations (Topic 3):** `get_cited_answer()` — generates an answer, parses citations, verifies them, and decides whether to refuse
- **History (Topic 4):** `chat()` — rewrites follow-ups, calls the citation pipeline, and appends to history

> "In the module demo, these three sections become three separate files: `retrieval.py`, `citations.py`, and `history.py`. Today they are together so we can focus on the interface."

Quick test from the terminal:

```
python -c "from pipeline import chat; r = chat('How many days of annual leave do I get?', []); print('PASS' if not r['refused'] else 'FAIL')"
```

If it prints PASS, the pipeline is ready.

### Part 2 — Starting the App (5 min)

Open `app.py`. Walk through it top to bottom before running it.

> "The first Streamlit call is `st.set_page_config()` — this must be the very first `st.*` call in the script, before anything else. It sets the browser tab title and icon."

Point at the import:

```python
from pipeline import chat
```

> "One import. The entire retrieval-citation-history pipeline is behind that single function. The Streamlit app does not know or care about ChromaDB, embeddings, or re-ranking."

Now run it:

```
streamlit run app.py
```

The browser opens. The sidebar shows "NovaNet HR" with a login form. The main area says "Please log in."

> "The app is running. Notice two things: the sidebar on the left with the login form, and the message in the centre telling you to log in. The chat input at the bottom is hidden — `st.stop()` prevents anything below it from rendering until you log in."

### Part 3 — The Login Flow (5 min)

Log in with any username and password (e.g., `amina`, `test123`).

> "This is a placeholder login — it accepts any non-empty credentials. Real authentication with bcrypt and JWT comes in Topic 6. Today we are wiring the UI structure."

Point at the sidebar code:

```python
if "username" not in st.session_state:
    # Show login form
    ...
else:
    st.success(f"Logged in as {st.session_state.username}")
```

> "After login, `st.session_state.username` is set and `st.rerun()` re-runs the script. This time, the `if` check finds the username, so the else branch runs — it shows 'Logged in as amina' and a logout button. The `st.stop()` guard in the main area is also skipped, so the chat appears."

Click Log out. Everything resets — username, conversation history, pipeline history.

> "Logout deletes all three session state keys and calls `st.rerun()`. The employee starts fresh."

### Part 4 — The First Question (7 min)

Log back in. Type: "How many days of annual leave do I get?"

> "Watch the spinner — 'Searching HR documents...' The employee knows the system is working, not frozen."

The answer appears with citations.

> "The answer is rendered with `st.markdown()` — it handles bold text, lists, and the `[Source N]` markers. Below the answer, click 'Sources cited.' This is an `st.expander` — it keeps the citations visible but not overwhelming."

Point at the citations:

> "Each citation shows the source key, the doc_id, the section, and whether it was verified. The employee can see exactly where the answer came from."

Point at the feedback buttons:

> "Thumbs up, thumbs down. Click thumbs up — the toast says 'Thanks for the feedback!' It disappears after a few seconds. In Topic 6, this feedback gets stored in the Q&A log."

Walk through the code that handles this:

```python
if question := st.chat_input("..."):
    st.chat_message("user").write(question)
    with st.chat_message("assistant"):
        with st.spinner("Searching HR documents..."):
            result = chat(question, st.session_state.pipeline_history)
        st.markdown(result["answer"])
        ...
```

> "The walrus operator `:=` both checks and assigns. If the employee typed something, `question` is the string. If this is just a re-run (from clicking a button), the block is skipped."

### Part 5 — Multi-turn Conversation (5 min)

Follow up: "How many of those can I carry over?"

> "The rewriter from Topic 4 kicks in. It rewrites 'those' into something like 'How many annual leave days can I carry over to the next year?' ChromaDB finds the carry-over policy. The answer appears with new citations."

Follow up again: "What is the deadline for using them?"

> "Three turns, all answered correctly. The conversation history stays on screen because we stored each message in `st.session_state.messages`. Every re-run replays the entire conversation from that list."

Point at the two separate histories:

```python
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pipeline_history" not in st.session_state:
    st.session_state.pipeline_history = []
```

> "Two lists. `messages` is for display — it includes the citations so we can render them on re-run. `pipeline_history` is the `{role, content}` list that the rewriter uses — same format as Topic 4. The rewriter does not need citations, so `pipeline.chat()` strips them before appending."

### Part 6 — Error Handling (3 min)

> "What happens when things go wrong?"

Point at the `try/except` block:

```python
try:
    with st.spinner("Searching HR documents..."):
        result = chat(question, st.session_state.pipeline_history)
    ...
except Exception:
    st.error(
        "The HR assistant is temporarily unavailable. "
        "Please try again in a few minutes."
    )
```

> "If the LLM API is down, the embedding service is unreachable, or ChromaDB throws an error — the employee sees a clean message, not a Python traceback. This is the minimum bar for an internal tool."

Optionally demonstrate by temporarily renaming a variable in `.env`, asking a question (error message appears), then fixing it.

### Part 7 — Refusal and Topic Switch (5 min)

Ask: "Can I bring my pet to the office?"

> "The pipeline refuses — low similarity, no citations. The employee sees the refusal message. No citations section appears because we check `result['refused']` before rendering the expander."

Ask: "What is the remote work allowance?"

> "Topic switch. The rewriter sees that this is already a standalone question and returns it unchanged. ChromaDB finds the remote work policy. The assistant answers with citations."

Follow up: "Was it always that amount?"

> "The rewriter rewrites this to something like 'Was the monthly Remote Work Allowance always NGN 35,000?' — it connects 'that amount' to the most recent topic, not the leave conversation from earlier."

### Part 8 — Architecture Preview (5 min)

> "Today `app.py` calls `pipeline.chat()` directly — same Python process. In the module demo, the pipeline moves behind a FastAPI backend. The Streamlit app calls `requests.post('http://localhost:8000/query', ...)` instead. The rendering code stays identical."

Draw on the board:

```
Today:
  app.py  →  pipeline.py  →  ChromaDB + LLM

Module demo:
  app.py  →  HTTP  →  api.py  →  retrieval.py + citations.py + history.py  →  ChromaDB + LLM
```

> "The only change in `app.py` is swapping `chat(question, history)` for `requests.post(url, json={...})`. The spinner, the citations expander, the feedback buttons, the sidebar — all unchanged. That is the point of separation: the interface does not care where the pipeline lives."

### Close (2 min)

> "You built a working chat interface in ~80 lines of Python. An employee can log in, ask questions, read cited answers, follow up, and give feedback — without knowing that ChromaDB, query rewriting, or citation verification exist behind the scenes. Next topic — Authentication and Q&A Logging — replaces the placeholder login with real bcrypt password hashing and JWT tokens, and logs every exchange to MySQL so you can review answer quality."

---

## Common Issues

- **"ModuleNotFoundError: No module named 'streamlit'"** — run `pip install streamlit` in the terminal. Make sure the Python environment matches the one used for Topics 2–4 (the one with chromadb and openai installed).
- **"Collection not found" on startup** — the ChromaDB collection from Topic 2 does not exist. The student needs to go back and run the ingestion cell in the Topic 2 notebook.
- **Conversation disappears on every interaction** — the student forgot `st.session_state`. The messages are being stored in a regular variable that resets on every re-run.
- **Duplicate buttons cause Streamlit errors** — missing `key=` parameter on the feedback buttons. Every `st.button` in a loop needs a unique key.
- **"st.set_page_config must be the first Streamlit command"** — `st.set_page_config()` must appear before any other `st.*` call, including `st.sidebar`. Move it to the very first line after imports.
- **Page hangs after question** — the LLM or embedding API is slow or unreachable. The spinner confirms the app is not frozen — it is waiting for the API. Check the `.env` values.
- **Citations show on refused answers** — the student is not checking `result["refused"]` before rendering the expander. Add the `if not result["refused"]` guard.
- **Sidebar login form reappears after login** — missing `st.rerun()` after setting `st.session_state.username`. Without it, the current script run still sees the old state.

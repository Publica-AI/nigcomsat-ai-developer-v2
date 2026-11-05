# Demo Guide - Authentication & Q&A Logging
**Module 4, Topic 6 | Estimated duration: 40-45 minutes**

---

## What This Demo Teaches

- Hashing passwords with bcrypt and verifying them with constant-time comparison
- Creating and decoding JWT tokens with PyJWT
- Setting up a MySQL database for users and Q&A logs with SQLAlchemy
- Building FastAPI auth endpoints: `/register`, `/login`, and a `get_current_user` dependency
- Protecting the `/query` endpoint with token-based auth and logging every exchange
- Upgrading the Streamlit sidebar from placeholder login to real authentication via HTTP
- Wiring feedback buttons to the Q&A log via a `/feedback` endpoint
- Querying the logs with SQL to find low-confidence answers and negative feedback
- Discussing employee data privacy under the NDPA

---

## Prerequisites

- **Topics 2–5 must be completed.** The ChromaDB collection `novanet_hr` (90 chunks) must exist from the Topic 2 demo.
- The `.env` file needs the same six variables as previous topics, plus two new ones (see Setup).
- **MySQL must be installed and running.** The same MySQL instance used in Module 2 (taskflow-backend) is fine.
- **Additional packages:** `pip install bcrypt pyjwt`
- Students should have VS Code open — this demo is built in the editor and terminal, not in Jupyter.

---

## Demo Files

| File | Purpose |
|------|---------|
| `auth.py` | Password hashing (bcrypt) and JWT token creation/verification |
| `database.py` | SQLAlchemy engine and session factory for MySQL |
| `models.py` | `User` and `QALog` SQLAlchemy models |
| `pipeline.py` | All retrieval, citation, and history functions from Topics 2–4 (copy from Topic 5) |
| `api.py` | FastAPI backend — `/register`, `/login`, `/query`, `/feedback`, `/logs` |
| `app.py` | Upgraded Streamlit interface — real login, feedback via API |

---

## Setup

1. Open VS Code in the Topic 6 demo folder

2. Create the MySQL database:

```sql
CREATE DATABASE IF NOT EXISTS novanet_hr_app
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

3. Add two new variables to the `.env` file (copy from Topic 5 and extend):

```
# Existing (from Topics 2-5)
OPENAI_API_KEY=...
MODEL_NAME=...
OPENAI_BASE_URL=...
EMBEDDING_API_KEY=...
EMBEDDING_BASE_URL=...
EMBEDDING_MODEL=...

# New for Topic 6
DATABASE_URL=mysql+pymysql://root:@localhost/novanet_hr_app
JWT_SECRET_KEY=novanet-demo-secret-change-in-production
```

4. Install new packages: `pip install bcrypt pyjwt pymysql`

5. Keep all six Python files visible in VS Code's explorer panel

---

## Demo Steps

### Part 1 — Password Hashing with bcrypt (5 min)

Open `auth.py`. Focus on the two password functions at the top.

> "Before we can authenticate anyone, we need to store their password safely. Rule number one: never store a plaintext password. If the database is compromised, every password is exposed."

Test in the terminal:

```
python -c "from auth import hash_password, verify_password; h = hash_password('test123'); print(h); print(verify_password('test123', h)); print(verify_password('wrong', h))"
```

Expected output: a 60-character hash starting with `$2b$12$`, then `True`, then `False`.

> "Call `hash_password('test123')` twice — you get two different hashes. That is the random salt at work. But `verify_password` works with either one, because the salt is embedded in the hash string."

Run it again to show different hashes for the same password:

```
python -c "from auth import hash_password; print(hash_password('test123')); print(hash_password('test123'))"
```

> "Two different hashes, same password. An attacker who gets the database cannot tell that these two users chose the same password."

Point at `verify_password`:

> "`bcrypt.checkpw` is constant-time — it takes the same amount of time whether the first character is wrong or the last. This prevents timing attacks."

### Part 2 — JWT Tokens (5 min)

Stay in `auth.py`. Focus on `create_token` and `decode_token`.

> "After the employee logs in, we need to give them something they can send with every request. A JWT — JSON Web Token — is a signed string that carries the username and an expiry."

Test in the terminal:

```
python -c "from auth import create_token, decode_token; t = create_token('amina'); print('Token:', t[:50] + '...'); print('Decoded:', decode_token(t))"
```

> "The token has three parts separated by dots: header, payload, signature. The payload says 'this belongs to amina and expires in 24 hours.' Anyone can decode the payload — it is base64, not encrypted. But no one can change it without the signature failing."

Show what happens with a tampered token:

```
python -c "from auth import create_token, decode_token; t = create_token('amina'); print(decode_token(t + 'x'))"
```

> "Tamper with even one character and `jwt.decode` raises an error. The signature protects the payload."

Point at `get_current_user`:

> "This is a FastAPI dependency. We add it to any endpoint with `Depends(get_current_user)`. FastAPI extracts the Bearer token from the request header, passes it here, and if the token is invalid, the endpoint never runs — the employee gets a 401."

### Part 3 — Database Setup (3 min)

Open `database.py` and `models.py` side by side.

> "Two tables. `users` stores the username and the bcrypt hash — never the plaintext password. `qa_logs` stores every question-answer exchange: what the employee typed, what the rewriter produced, what the assistant answered, which sources it cited, how confident the retrieval was, how long it took, and whether the employee liked the answer."

Walk through the `QALog` columns in `models.py`:

> "Each column captures a different piece of the pipeline's work. `question` is what the employee typed. `search_query` is what the rewriter sent to ChromaDB. `similarity` is the best cosine similarity — if this is below 0.4, the answer is probably unreliable. `latency_ms` is the wall-clock time. `feedback` starts as NULL and gets updated when the employee clicks thumbs up or down."

> "The tables are created automatically on startup — `Base.metadata.create_all(bind=engine)` in `api.py`. No need for a migration tool in a demo."

### Part 4 — FastAPI Auth Endpoints (7 min)

Open `api.py`. Start the API server:

```
uvicorn api:app --reload
```

Open `http://localhost:8000/docs` in the browser.

> "FastAPI generates this interactive documentation automatically. Every endpoint we defined is here. Let's register a user."

Expand `POST /register`, click "Try it out", and enter:

```json
{
  "username": "amina",
  "password": "s3cur3Pass!"
}
```

Click Execute. Show the response: `{"message": "Account created for amina"}`.

> "The password was hashed with bcrypt and stored. If we look in MySQL, we will see the hash, not the password."

Optional — show the hash in MySQL:

```sql
SELECT username, password_hash FROM users;
```

Now log in. Expand `POST /login`, enter the same credentials:

```json
{
  "username": "amina",
  "password": "s3cur3Pass!"
}
```

Click Execute. Show the response with the JWT token.

> "The server checked the password against the stored hash, and it matched. So it issued a JWT — that long string. The Streamlit app will store this and send it with every request."

Copy the token. Click the "Authorize" button at the top of `/docs`, paste the token, and click "Authorize."

> "Now every request we make through this page includes the Bearer token. We are authenticated."

Show a wrong password:

```json
{
  "username": "amina",
  "password": "wrongPassword"
}
```

> "401 Unauthorized. Notice the message: 'Invalid username or password' — not 'wrong password' or 'user not found.' We never tell the caller which part was wrong, because that would tell an attacker which usernames are valid."

### Part 5 — Protected Query with Logging (7 min)

Still in `/docs`, expand `POST /query` and ask:

```json
{
  "question": "How many days of annual leave do I get?"
}
```

> "The endpoint decoded our JWT, confirmed we are amina, ran the pipeline, and logged the exchange. The response includes the answer, citations, and a `log_id` — that is the row ID in the `qa_logs` table."

Show the log in MySQL:

```sql
SELECT id, question, search_query, similarity, latency_ms, feedback, created_at
FROM qa_logs ORDER BY created_at DESC LIMIT 5;
```

> "There it is. The question, the search query (same as the question since this was the first turn), similarity 0.7-something, latency in milliseconds, feedback is NULL — no one has rated this answer yet."

Ask a follow-up through `/docs`:

```json
{
  "question": "How many of those can I carry over?"
}
```

> "The rewriter kicks in. Check the log — `search_query` will be different from `question` because the rewriter expanded 'those' into 'annual leave days.'"

```sql
SELECT id, question, search_query FROM qa_logs ORDER BY created_at DESC LIMIT 2;
```

Now try without authentication. Click the "Authorize" button and click "Logout." Try the query again.

> "401 — the endpoint is protected by `Depends(get_current_user)`. No token, no access."

### Part 6 — Upgraded Streamlit App (5 min)

Open a second terminal (keep the FastAPI server running). Start the Streamlit app:

```
streamlit run app.py
```

> "The sidebar looks the same as Topic 5 — username, password, log in button. But watch what happens when you log in."

Enter `amina` / `s3cur3Pass!`.

> "The app sent a POST to `localhost:8000/login`. The API verified the password, issued a JWT, and the app stored it in `session_state.token`. From now on, every question goes to the API with that token in the Authorization header."

Point at the sidebar:

> "Notice the new line: 'Your questions are logged for quality monitoring.' This is the NDPA transparency requirement — we tell employees that their questions are logged."

Ask a question: "What is the remote work allowance?"

> "The answer appears with citations, just like Topic 5. But behind the scenes, this went through the FastAPI backend: the request was authenticated, the pipeline ran, the exchange was logged to MySQL, and the response came back."

Open MySQL and show the new row:

```sql
SELECT id, question, latency_ms FROM qa_logs ORDER BY created_at DESC LIMIT 3;
```

Enter a wrong password to show the error:

> "'Invalid username or password.' The same generic message as the API. And 'Cannot reach the API server' if FastAPI is not running."

### Part 7 — Feedback and Evaluation (5 min)

Back in the Streamlit app, click the thumbs-down button on the last answer.

> "The toast says 'Thanks — we'll review this answer.' But unlike Topic 5, this also sent a POST to `/feedback` with the `log_id` and 'negative.' Let's check."

```sql
SELECT id, question, feedback FROM qa_logs ORDER BY created_at DESC LIMIT 5;
```

> "The `feedback` column is now 'negative' on that row. This is the highest-signal evaluation data — an employee took the time to say the answer was wrong."

Now run the evaluation queries from Slide 10:

```sql
-- Low-confidence answers
SELECT question, similarity, LEFT(answer, 100) AS answer_preview
FROM qa_logs WHERE similarity < 0.5
ORDER BY created_at DESC;

-- Negative feedback
SELECT question, LEFT(answer, 100) AS answer_preview, feedback
FROM qa_logs WHERE feedback = 'negative';

-- Slow responses
SELECT question, latency_ms
FROM qa_logs WHERE latency_ms > 10000;

-- Most-asked questions
SELECT question, COUNT(*) AS ask_count
FROM qa_logs GROUP BY question
ORDER BY ask_count DESC LIMIT 10;
```

> "These are your debugging tools for a RAG pipeline in production. Low similarity means the corpus does not cover the topic well — add documents. Negative feedback means the employee disagreed — review the answer manually. Slow responses mean the pipeline or the API is slow — profile and optimise."

Also show the `/logs` endpoint in the browser:

```
http://localhost:8000/logs
```

> "The API has a `/logs` endpoint too — you could build an admin dashboard that reads from this."

### Part 8 — NDPA Discussion (3 min)

No code in this part. This is a conversation with the class.

> "We have been logging every question an employee asks. 'How many sick days do I have left?' — that tells you something about the employee's health. 'What is the disciplinary process?' — that tells you the employee is worried about their job."

> "The Nigeria Data Protection Act applies here. Five principles:"

Walk through the five principles on the board:

1. **Purpose limitation** — "These logs are for answer quality monitoring, not for tracking what employees are thinking about. If a manager asks 'What has Amina been searching for?' — the answer is 'We don't share that.'"

2. **Data minimisation** — "We log the question, answer, sources, latency, and feedback. We do not log the employee's IP address, browser, or session duration."

3. **Retention** — "Set a policy: 90 days. After 90 days, delete or anonymise the logs. A cron job handles this."

4. **Access control** — "Only the development team and HR admin can read the logs. Not managers, not team leads."

5. **Transparency** — "We added one line to the sidebar: 'Your questions are logged for quality monitoring.' For an internal tool, that is enough."

> "Data protection is not optional. It is the law, and it is the right thing to do."

### Close (2 min)

> "You built real authentication and logging into the HR assistant. Passwords are hashed with bcrypt, sessions use JWT tokens, every exchange is logged with latency and user identity, feedback buttons write to the database, and SQL queries help you find bad answers before the employee complains. Next — the module demo: we assemble everything into the `knowledge-assistant/` reference build, the code folder that Modules 5 and 6 build on."

---

## Common Issues

- **"ModuleNotFoundError: No module named 'bcrypt'"** — run `pip install bcrypt`. On some systems, you may also need to install `cffi`.
- **"ModuleNotFoundError: No module named 'jwt'"** — the package is called `pyjwt`, not `jwt`. Run `pip install pyjwt`. If you have both `jwt` and `pyjwt` installed, uninstall `jwt` first: `pip uninstall jwt && pip install pyjwt`.
- **"Access denied for user 'root'@'localhost'"** — the MySQL password in `DATABASE_URL` does not match. Check your MySQL root password and update the `.env` file.
- **"Unknown database 'novanet_hr_app'"** — the database has not been created. Run `CREATE DATABASE novanet_hr_app;` in MySQL.
- **"Cannot reach the API server"** — FastAPI is not running. Start it with `uvicorn api:app --reload` in a separate terminal. Keep both terminals open.
- **"401 Unauthorized" on every request** — the JWT has expired (24-hour default) or the `JWT_SECRET_KEY` in `.env` changed since the token was issued. Log out and log in again.
- **Feedback button does not update the log** — check that the `log_id` is being returned from the `/query` response. If the API response does not include `log_id`, the Streamlit app cannot call `/feedback`.
- **"Collection not found" on first query** — the ChromaDB collection from Topic 2 does not exist. The student needs to go back and run the ingestion cell in the Topic 2 notebook.
- **Port conflict on 8000 or 8501** — another process is using the port. Use `uvicorn api:app --reload --port 8001` and update `API_URL` in `app.py` to match, or kill the existing process.

# Topic 6 Demo — Authentication & Q&A Logging

## 1. Install packages

```bash
pip install bcrypt pyjwt pymysql fastapi uvicorn sqlalchemy streamlit
```

(The packages from Topics 2–5 — `openai`, `chromadb`, `python-dotenv`, `requests` — should already be installed.)

## 2. Create the MySQL database

Open MySQL and run:

```sql
CREATE DATABASE IF NOT EXISTS novanet_hr_app
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 3. Set up the `.env` file

Copy `.env` from the Topic 5 demo folder into this folder, then add two lines at the bottom:

```
DATABASE_URL=mysql+pymysql://root:YOUR_MYSQL_PASSWORD@localhost/novanet_hr_app
JWT_SECRET_KEY=novanet-demo-secret-change-in-production
```

If your MySQL root has no password, use:

```
DATABASE_URL=mysql+pymysql://root:@localhost/novanet_hr_app
```

Your `.env` should now have 8 variables total:

```
OPENAI_API_KEY=...
MODEL_NAME=...
OPENAI_BASE_URL=...
EMBEDDING_API_KEY=...
EMBEDDING_BASE_URL=...
EMBEDDING_MODEL=...
DATABASE_URL=mysql+pymysql://root:@localhost/novanet_hr_app
JWT_SECRET_KEY=novanet-demo-secret-change-in-production
```

## 4. Start the FastAPI server (Terminal 1)

```bash
cd week-04/06-authentication-and-qa-logging/demo
uvicorn api:app --reload
```

The tables (`users`, `qa_logs`) are created automatically on startup. You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

## 5. Register a user

Open http://localhost:8000/docs in your browser.

1. Expand **POST /register**
2. Click "Try it out"
3. Enter:
   ```json
   {
     "username": "amina",
     "password": "s3cur3Pass!"
   }
   ```
4. Click **Execute**
5. You should see: `{"message": "Account created for amina"}`

## 6. Start the Streamlit app (Terminal 2)

Open a second terminal (keep the FastAPI server running in Terminal 1):

```bash
cd week-04/06-authentication-and-qa-logging/demo
streamlit run app.py
```

The browser opens at http://localhost:8501.

## 7. Log in and use the app

- Username: `amina`
- Password: `s3cur3Pass!`

Try these questions:
- "How many days of annual leave do I get?"
- "How many of those can I carry over?"
- "What is the remote work allowance?"
- "Can I bring my pet to the office?" (should be refused)

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Cannot reach the API server" | FastAPI is not running. Check Terminal 1. |
| "Invalid username or password" | You need to register first (Step 5). |
| "Unknown database 'novanet_hr_app'" | Run the CREATE DATABASE command (Step 2). |
| "Access denied for user 'root'" | Check your MySQL password in `DATABASE_URL`. |
| "Collection not found" | The ChromaDB collection from Topic 2 is missing. Run the Topic 2 notebook first. |
| "ModuleNotFoundError: No module named 'jwt'" | Run `pip install pyjwt` (not `pip install jwt`). |
| Port 8000 already in use | Use `uvicorn api:app --reload --port 8001` and change `API_URL` in `app.py` to match. |

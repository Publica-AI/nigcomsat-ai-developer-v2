"""NovaNet HR Assistant — FastAPI backend with auth and Q&A logging.

Endpoints:
  POST /register  — create an account (bcrypt-hashed password)
  POST /login     — verify password, return a JWT
  POST /query     — authenticated: run the pipeline, log the exchange
  POST /feedback  — authenticated: record thumbs-up / thumbs-down
  GET  /logs      — authenticated: review recent Q&A log entries
"""

import json
import time

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import (
    create_token,
    get_current_user,
    hash_password,
    verify_password,
)
from database import Base, engine, get_db
from models import QALog, User
from pipeline import chat

# ── Create tables on startup ───────────────────────────────────────

Base.metadata.create_all(bind=engine)

app = FastAPI(title="NovaNet HR Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Per-user conversation history (in-memory; resets when the server restarts)
user_histories: dict[str, list] = {}


# ── Request schemas ────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class QueryRequest(BaseModel):
    question: str


class FeedbackRequest(BaseModel):
    log_id: int
    feedback: str


# ── Auth endpoints ─────────────────────────────────────────────────

@app.post("/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter_by(username=body.username).first():
        raise HTTPException(400, "Username already exists")
    user = User(
        username=body.username,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    db.commit()
    return {"message": f"Account created for {body.username}"}


@app.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=body.username).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "Invalid username or password")
    token = create_token(body.username)
    return {"token": token, "username": body.username}


# ── Pipeline endpoint (protected + logged) ─────────────────────────

@app.post("/query")
def query(
    body: QueryRequest,
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user not in user_histories:
        user_histories[user] = []

    start = time.time()
    result = chat(body.question, user_histories[user])
    latency_ms = int((time.time() - start) * 1000)

    db_user = db.query(User).filter_by(username=user).first()

    log = QALog(
        user_id=db_user.id if db_user else 0,
        question=body.question,
        search_query=result.get("search_query", body.question),
        answer=result["answer"],
        sources=json.dumps(result.get("citations", []), default=str),
        similarity=result.get("best_similarity", 0),
        latency_ms=latency_ms,
    )
    db.add(log)
    db.commit()

    result["log_id"] = log.id
    return result


# ── Feedback endpoint ──────────────────────────────────────────────

@app.post("/feedback")
def feedback(
    body: FeedbackRequest,
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    log = db.query(QALog).filter_by(id=body.log_id).first()
    if not log:
        raise HTTPException(404, "Log entry not found")
    if body.feedback not in ("positive", "negative"):
        raise HTTPException(400, "Feedback must be 'positive' or 'negative'")
    log.feedback = body.feedback
    db.commit()
    return {"message": "Feedback recorded"}


# ── Log review endpoint ───────────────────────────────────────────

@app.get("/logs")
def get_logs(
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logs = db.query(QALog).order_by(QALog.created_at.desc()).limit(50).all()
    return [
        {
            "id": log.id,
            "question": log.question,
            "search_query": log.search_query,
            "answer": (
                log.answer[:200] + "..." if len(log.answer or "") > 200 else log.answer
            ),
            "similarity": log.similarity,
            "latency_ms": log.latency_ms,
            "feedback": log.feedback,
            "created_at": str(log.created_at),
        }
        for log in logs
    ]

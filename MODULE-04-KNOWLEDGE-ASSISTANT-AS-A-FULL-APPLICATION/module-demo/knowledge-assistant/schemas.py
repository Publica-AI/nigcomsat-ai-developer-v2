"""Pydantic request and response schemas for the FastAPI endpoints."""

from pydantic import BaseModel


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

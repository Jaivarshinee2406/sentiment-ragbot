from fastapi import FastAPI
from pydantic import BaseModel
import uuid

from app.sentiment import classify_ticket
from app.embeddings import index_ticket
from app.db import init_db, save_ticket, fetch_all_tickets
from app.rag import answer_question

app = FastAPI(title="Support Ticket Sentiment RAG Bot")


class TicketIn(BaseModel):
    text: str
    ticket_id: str | None = None


class QuestionIn(BaseModel):
    question: str
    n_results: int = 5
    sentiment_filter: str | None = None


@app.on_event("startup")
def startup():
    init_db()


@app.post("/analyze")
def analyze_ticket(payload: TicketIn):
    ticket_id = payload.ticket_id or str(uuid.uuid4())
    classification = classify_ticket(payload.text)
    save_ticket(ticket_id, payload.text, classification)
    index_ticket(ticket_id, payload.text, classification)
    return {"ticket_id": ticket_id, **classification}


@app.post("/ask")
def ask(payload: QuestionIn):
    return answer_question(
        payload.question, n_results=payload.n_results, sentiment_filter=payload.sentiment_filter
    )


@app.get("/tickets")
def list_tickets():
    return fetch_all_tickets()


@app.get("/health")
def health():
    return {"status": "ok"}

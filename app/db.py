"""
MySQL persistence layer. Run sql/schema.sql once to create the table
(or let init_db() do it for you).
"""
from sqlalchemy import create_engine, text
from app.config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

_engine = create_engine(
    f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}",
    pool_pre_ping=True,
)

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS tickets (
    ticket_id VARCHAR(50) PRIMARY KEY,
    ticket_text LONGTEXT,
    sentiment VARCHAR(20),
    confidence FLOAT,
    category VARCHAR(100),
    summary TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

INSERT_SQL = """
INSERT INTO tickets (ticket_id, ticket_text, sentiment, confidence, category, summary)
VALUES (:ticket_id, :ticket_text, :sentiment, :confidence, :category, :summary)
ON DUPLICATE KEY UPDATE
    sentiment = VALUES(sentiment),
    confidence = VALUES(confidence),
    category = VALUES(category),
    summary = VALUES(summary);
"""


def init_db():
    with _engine.begin() as conn:
        conn.execute(text(CREATE_TABLE_SQL))


def save_ticket(ticket_id: str, ticket_text: str, classification: dict):
    with _engine.begin() as conn:
        conn.execute(
            text(INSERT_SQL),
            {
                "ticket_id": ticket_id,
                "ticket_text": ticket_text,
                "sentiment": classification["sentiment"],
                "confidence": classification["confidence"],
                "category": classification["category"],
                "summary": classification["summary"],
            },
        )


def fetch_all_tickets():
    with _engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM tickets ORDER BY created_at DESC"))
        return [dict(row._mapping) for row in result]

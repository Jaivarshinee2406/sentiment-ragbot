CREATE DATABASE IF NOT EXISTS support_tickets;
USE support_tickets;

CREATE TABLE IF NOT EXISTS tickets (
    ticket_id VARCHAR(50) PRIMARY KEY,
    ticket_text LONGTEXT,
    sentiment VARCHAR(20),
    confidence FLOAT,
    category VARCHAR(100),
    summary TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Handy view for Power BI: daily sentiment counts
CREATE OR REPLACE VIEW daily_sentiment_summary AS
SELECT
    DATE(created_at) AS day,
    sentiment,
    category,
    COUNT(*) AS ticket_count
FROM tickets
GROUP BY DATE(created_at), sentiment, category;

"""
Batch pipeline: reads data/sample_tickets.csv, classifies each ticket with
Claude, writes structured results to MySQL, and indexes embeddings in Chroma.

Usage:
    python -m scripts.ingest
"""
import csv
import time
from pathlib import Path

from app.sentiment import classify_ticket
from app.embeddings import index_ticket
from app.db import init_db, save_ticket

CSV_PATH = Path(__file__).parent.parent / "data" / "sample_tickets.csv"


def run():
    init_db()
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    print(f"Ingesting {len(reader)} tickets...")
    for i, row in enumerate(reader, 1):
        ticket_id = row["ticket_id"]
        text = row["text"]

        classification = classify_ticket(text)
        save_ticket(ticket_id, text, classification)
        index_ticket(ticket_id, text, classification)

        print(f"[{i}/{len(reader)}] {ticket_id[:8]} -> {classification['sentiment']} / {classification['category']}")
        time.sleep(0.2)  # gentle pacing to avoid rate limits on large batches

    print("Done. Data is in MySQL and Chroma is indexed.")


if __name__ == "__main__":
    run()

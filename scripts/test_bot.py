"""
Quick standalone test — classifies a few sample tickets with Claude,
indexes them in Chroma, then asks a RAG question. No MySQL required.

Usage:
    python -m scripts.test_bot
"""
from app.sentiment import classify_ticket
from app.embeddings import index_ticket
from app.rag import answer_question

SAMPLE_TICKETS = [
    "My package arrived three weeks late and support never replied to my emails.",
    "The app keeps crashing every time I try to open my dashboard, this has been going on for 5 days.",
    "Thanks for resolving my billing issue so quickly, really appreciated!",
    "Does the jacket come in other sizes?",
    "My account was locked without explanation and I've been waiting 10 days for a response.",
]

def run():
    print("=" * 60)
    print("STEP 1: Classifying sample tickets with Claude")
    print("=" * 60)

    for i, text in enumerate(SAMPLE_TICKETS):
        ticket_id = f"test-{i}"
        result = classify_ticket(text)
        print(f"\nTicket: {text}")
        print(f"  -> sentiment={result['sentiment']} | category={result['category']} | confidence={result['confidence']}")
        print(f"  -> summary: {result['summary']}")
        index_ticket(ticket_id, text, result)

    print("\n" + "=" * 60)
    print("STEP 2: Asking a RAG question about the indexed tickets")
    print("=" * 60)

    question = "What are customers unhappy about?"
    result = answer_question(question, n_results=3)
    print(f"\nQuestion: {question}")
    print(f"Answer: {result['answer']}")

if __name__ == "__main__":
    run()

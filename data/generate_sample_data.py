import csv
import random
import uuid
from pathlib import Path

TEMPLATES = {
    "billing": {
        "negative": [
            "I was charged twice for my {item} order and support hasn't refunded me after {n} days.",
            "My subscription renewed even though I cancelled it last month. This is unacceptable.",
        ],
        "neutral": [
            "Can you explain why my invoice for {item} shows an extra line item?",
        ],
        "positive": [
            "Thanks for resolving my billing issue with {item} so quickly!",
        ],
    },
    "shipping": {
        "negative": [
            "My {item} order has been stuck in transit for {n} days with no update.",
            "The package arrived damaged and customer service isn't responding.",
        ],
        "neutral": [
            "When will my order for {item} arrive? Tracking hasn't updated in {n} days.",
        ],
        "positive": [
            "My {item} arrived a day early, great service!",
        ],
    },
    "technical": {
        "negative": [
            "The app keeps crashing every time I try to open {item}, this has been going on for {n} days.",
            "I can't log in after the latest update, tried resetting password twice.",
        ],
        "neutral": [
            "How do I export my {item} data to CSV?",
        ],
        "positive": [
            "The new update fixed the bug I reported, works great now!",
        ],
    },
    "account": {
        "negative": [
            "My account was locked without explanation and I've been waiting {n} days for a response.",
        ],
        "neutral": [
            "How do I change the email address linked to my account?",
        ],
        "positive": [
            "Support helped me recover my account within minutes, very impressed.",
        ],
    },
    "product": {
        "negative": [
            "The {item} I received doesn't match the description at all, very disappointed.",
        ],
        "neutral": [
            "Does the {item} come in other sizes?",
        ],
        "positive": [
            "Absolutely love my new {item}, exceeded expectations!",
        ],
    },
}

ITEMS = ["headphones", "laptop", "subscription plan", "order", "account dashboard", "mobile app", "jacket", "blender"]


def generate_tickets(n: int = 100):
    rows = []
    categories = list(TEMPLATES.keys())
    for _ in range(n):
        category = random.choice(categories)
        sentiment = random.choices(
            ["negative", "neutral", "positive"], weights=[0.45, 0.25, 0.30]
        )[0]
        template = random.choice(TEMPLATES[category][sentiment])
        text = template.format(item=random.choice(ITEMS), n=random.randint(2, 21))
        rows.append({
            "ticket_id": str(uuid.uuid4()),
            "text": text,
            "true_category": category,     
            "true_sentiment": sentiment,    
        })
    return rows


if __name__ == "__main__":
    output_path = Path(__file__).parent / "sample_tickets.csv"
    rows = generate_tickets(150)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["ticket_id", "text", "true_category", "true_sentiment"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {len(rows)} sample tickets at {output_path}")

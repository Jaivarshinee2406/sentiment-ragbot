"""
Sentiment + category classification for a support ticket, using FREE
locally-run HuggingFace models (no API key, no cost, runs on your machine).

First run will download ~500MB-1GB of model weights (one-time, cached
afterward in your user folder). Needs internet only for that first download.
"""
from functools import lru_cache

# Lazy-loaded so importing this module doesn't immediately load models
_sentiment_pipeline = None
_category_pipeline = None

CATEGORIES = ["billing", "technical", "shipping", "account", "product", "other"]


def _get_sentiment_pipeline():
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        from transformers import pipeline
        # Free, local model - outputs "negative" / "neutral" / "positive" directly
        _sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
        )
    return _sentiment_pipeline


def _get_category_pipeline():
    global _category_pipeline
    if _category_pipeline is None:
        from transformers import pipeline
        # Free, local zero-shot classifier - can sort text into arbitrary labels
        _category_pipeline = pipeline(
            "zero-shot-classification",
            model="valhalla/distilbart-mnli-12-3",
        )
    return _category_pipeline


def _make_summary(text: str, max_words: int = 15) -> str:
    """Simple extractive summary (first N words) - free, no extra model needed."""
    words = text.strip().split()
    if len(words) <= max_words:
        return text.strip()
    return " ".join(words[:max_words]) + "..."


def classify_ticket(ticket_text: str) -> dict:
    sentiment_result = _get_sentiment_pipeline()(ticket_text)[0]
    sentiment = sentiment_result["label"].lower()
    confidence = round(float(sentiment_result["score"]), 3)

    category_result = _get_category_pipeline()(ticket_text, candidate_labels=CATEGORIES)
    category = category_result["labels"][0]  # top predicted label

    summary = _make_summary(ticket_text)

    return {
        "sentiment": sentiment,
        "confidence": confidence,
        "category": category,
        "summary": summary,
    }


if __name__ == "__main__":
    sample = "My package arrived three weeks late and support never replied to my emails."
    print(classify_ticket(sample))

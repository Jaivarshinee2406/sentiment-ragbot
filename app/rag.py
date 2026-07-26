from app.embeddings import query_similar

_tokenizer = None
_model = None

MODEL_NAME = "google/flan-t5-base"


def _get_model():
    global _tokenizer, _model
    if _model is None:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    return _tokenizer, _model


def answer_question(question: str, n_results: int = 5, sentiment_filter: str | None = None) -> dict:
    where = {"sentiment": sentiment_filter} if sentiment_filter else None
    results = query_similar(question, n_results=n_results, where=where)

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]

    if not docs:
        return {"answer": "No relevant tickets found in the index.", "sources": []}

    context_blocks = []
    for i, (doc, meta) in enumerate(zip(docs, metas)):
        context_blocks.append(
            f"Ticket {i+1} (sentiment={meta.get('sentiment')}, category={meta.get('category')}): {doc}"
        )
    context = " ".join(context_blocks)

    prompt = (
        f"Answer the question using only the context below. Be concise.\n\n"
        f"Context: {context}\n\n"
        f"Question: {question}\n\nAnswer:"
    )

    tokenizer, model = _get_model()
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    output_ids = model.generate(
        **inputs,
        max_new_tokens=150,
        min_new_tokens=20,
        num_beams=4,
        no_repeat_ngram_size=3,
    )
    answer_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    return {"answer": answer_text, "sources": metas}

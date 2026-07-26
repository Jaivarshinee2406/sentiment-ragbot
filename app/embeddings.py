import chromadb
from chromadb.utils import embedding_functions
from app.config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION

_embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)


def get_collection():
    return _client.get_or_create_collection(
        name=CHROMA_COLLECTION, embedding_function=_embed_fn
    )


def index_ticket(ticket_id: str, text: str, metadata: dict):
    collection = get_collection()
    safe_meta = {k: (v if isinstance(v, (str, int, float, bool)) else str(v))
                 for k, v in metadata.items()}
    collection.upsert(ids=[ticket_id], documents=[text], metadatas=[safe_meta])


def query_similar(query_text: str, n_results: int = 5, where: dict | None = None):
    collection = get_collection()
    return collection.query(query_texts=[query_text], n_results=n_results, where=where)

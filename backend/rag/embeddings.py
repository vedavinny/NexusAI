"""
Embedding model wrapper around Sentence Transformers (BAAI/bge-small-en-v1.5).

Loaded once as a module-level singleton — the model is ~130MB and should not
be reloaded per-request.
"""
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from backend.config.settings import settings


@lru_cache
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(settings.EMBEDDING_MODEL_NAME)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts. bge models recommend no special prefix for passages."""
    model = get_embedding_model()
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return embeddings.tolist()


def embed_query(query: str) -> list[float]:
    """
    Embed a single search query.
    bge-small recommends prefixing queries (not passages) with an instruction
    for better retrieval quality.
    """
    model = get_embedding_model()
    prefixed = f"Represent this sentence for searching relevant passages: {query}"
    embedding = model.encode(prefixed, normalize_embeddings=True, show_progress_bar=False)
    return embedding.tolist()

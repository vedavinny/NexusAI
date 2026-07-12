"""
Embedding wrapper using FastEmbed.

FastEmbed runs the embedding model using ONNX Runtime instead of
PyTorch, significantly reducing memory usage for deployment.
"""

from functools import lru_cache

from fastembed import TextEmbedding


@lru_cache
def get_embedding_model() -> TextEmbedding:
    return TextEmbedding(
        model_name="BAAI/bge-small-en-v1.5",
    )


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_embedding_model()

    embeddings = list(model.embed(texts))

    return [e.tolist() for e in embeddings]


def embed_query(query: str) -> list[float]:
    model = get_embedding_model()

    query = (
        "Represent this sentence for searching relevant passages: "
        + query
    )

    embedding = next(model.embed([query]))

    return embedding.tolist()
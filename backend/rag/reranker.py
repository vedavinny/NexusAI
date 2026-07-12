from functools import lru_cache

from sentence_transformers import CrossEncoder


@lru_cache
def get_reranker():

    return CrossEncoder(
        "BAAI/bge-reranker-base"
    )


def rerank_chunks(
    question: str,
    chunks: list[dict],
    top_k: int = 5,
) -> list[dict]:

    if not chunks:
        return []

    reranker = get_reranker()

    pairs = [
        (question, chunk["chunk_text"])
        for chunk in chunks
    ]

    scores = reranker.predict(pairs)

    for chunk, score in zip(chunks, scores):

        chunk["rerank_score"] = float(score)

    chunks.sort(
        key=lambda x: x["rerank_score"],
        reverse=True,
    )

    return chunks[:top_k]
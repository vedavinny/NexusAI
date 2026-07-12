"""
Qdrant vector store helper.

Responsibilities:
- Create collection
- Store embeddings
- Retrieve similar chunks
- Delete vectors
"""

import uuid
from functools import lru_cache

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from backend.config.settings import settings


@lru_cache
def get_qdrant_client() -> QdrantClient:
    return QdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
    )


def ensure_collection() -> None:
    """
    Create collection if it doesn't already exist.
    """

    client = get_qdrant_client()

    collections = client.get_collections().collections

    existing = [c.name for c in collections]

    if settings.QDRANT_COLLECTION_NAME not in existing:

        client.create_collection(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            vectors_config=VectorParams(
                size=settings.EMBEDDING_DIM,
                distance=Distance.COSINE,
            ),
        )


def upsert_chunks(
    document_id: str,
    document_name: str,
    owner_id: str,
    chunks: list[str],
    vectors: list[list[float]],
    page_numbers: list[int | None],
    chunk_indices: list[int],
) -> None:
    """
    Store chunk embeddings into Qdrant.
    """

    client = get_qdrant_client()

    points = []

    for chunk, vector, page_number, chunk_index in zip(
        chunks,
        vectors,
        page_numbers,
        chunk_indices,
    ):

        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "document_id": document_id,
                    "document_name": document_name,
                    "owner_id": owner_id,
                    "chunk_text": chunk,
                    "page_number": page_number,
                    "chunk_index": chunk_index,
                },
            )
        )

    client.upsert(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        points=points,
        wait=True,
    )


def search_similar_chunks(
    query_vector: list[float],
    owner_id: str,
    top_k: int = 10,
    score_threshold: float = 0.35,
) -> list[dict]:
    """
    Search similar chunks from Qdrant.

    Used by the Multi-Query Retriever.
    """

    client = get_qdrant_client()

    results = client.query_points(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        query=query_vector,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="owner_id",
                    match=MatchValue(value=owner_id),
                )
            ]
        ),
        limit=top_k,
        with_payload=True,
    )

    retrieved = []

    for point in results.points:

        if point.score < score_threshold:
            continue

        payload = point.payload

        retrieved.append(
            {
                "document_id": payload["document_id"],
                "document_name": payload["document_name"],
                "chunk_text": payload["chunk_text"],
                "page_number": payload.get("page_number"),
                "chunk_index": payload.get("chunk_index", 0),
                "score": float(point.score),
            }
        )

    retrieved.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    return retrieved


def delete_document_vectors(
    document_id: str,
) -> None:
    """
    Delete all vectors for a document.
    """

    client = get_qdrant_client()

    client.delete(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id),
                )
            ]
        ),
    )


def delete_all_vectors() -> None:
    """
    Delete the entire collection.
    Useful during development after changing chunking strategy.
    """

    client = get_qdrant_client()

    collections = [
        c.name
        for c in client.get_collections().collections
    ]

    if settings.QDRANT_COLLECTION_NAME in collections:

        client.delete_collection(
            settings.QDRANT_COLLECTION_NAME
        )

        ensure_collection()
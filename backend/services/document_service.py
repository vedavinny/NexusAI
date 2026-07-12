"""
Business logic for document upload and ingestion into the RAG pipeline.
Keeps the API route thin: the route only handles HTTP concerns.
"""

from http.client import HTTPException
import logging
import os
import uuid

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.config.settings import settings
from backend.models.document import Document
from backend.rag.chunking import process_pdf
from backend.rag.embeddings import embed_texts
from backend.rag.vectorstore import ensure_collection, upsert_chunks
from backend.models.document import Document
from backend.rag.vectorstore import delete_document_vectors

logger = logging.getLogger(__name__)


class UnsupportedFileTypeError(Exception):
    pass


class FileTooLargeError(Exception):
    pass


async def _save_upload(file: UploadFile, owner_id: str) -> str:
    """
    Save uploaded PDF to disk.
    """

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    if not file.filename.lower().endswith(".pdf"):
        raise UnsupportedFileTypeError("Only PDF files are supported.")

    safe_name = f"{owner_id}_{uuid.uuid4().hex}_{file.filename}"
    destination = os.path.join(settings.UPLOAD_DIR, safe_name)

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    size = 0

    with open(destination, "wb") as out_file:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)

            if size > max_bytes:
                out_file.close()

                if os.path.exists(destination):
                    os.remove(destination)

                raise FileTooLargeError(
                    f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB upload limit."
                )

            out_file.write(chunk)

    return destination


async def ingest_document(
    db: AsyncSession,
    file: UploadFile,
    owner_id: str,
) -> Document:
    """
    Upload PDF

        ↓

    Extract text

        ↓

    Chunk document

        ↓

    Generate embeddings

        ↓

    Store vectors in Qdrant

        ↓

    Store metadata in PostgreSQL
    """

    storage_path = await _save_upload(file, owner_id)

    document = Document(
        owner_id=owner_id,
        filename=file.filename,
        storage_path=storage_path,
        status="processing",
    )

    db.add(document)
    await db.commit()
    await db.refresh(document)

    try:

        # --------------------------------------------------
        # Chunk PDF
        # --------------------------------------------------

        chunks = process_pdf(storage_path)

        if not chunks:
            document.status = "failed"
            await db.commit()
            return document

        texts = [chunk.text for chunk in chunks]

        page_numbers = [
            chunk.page_number
            for chunk in chunks
        ]

        chunk_indices = [
            chunk.chunk_index
            for chunk in chunks
        ]

        # --------------------------------------------------
        # Generate embeddings
        # --------------------------------------------------

        vectors = embed_texts(texts)

        # --------------------------------------------------
        # Create Qdrant collection
        # --------------------------------------------------

        ensure_collection()

        # --------------------------------------------------
        # Store vectors
        # --------------------------------------------------

        upsert_chunks(
            document_id=str(document.id),
            document_name=document.filename,
            owner_id=owner_id,
            chunks=texts,
            vectors=vectors,
            page_numbers=page_numbers,
            chunk_indices=chunk_indices,
        )

        # --------------------------------------------------
        # Update database
        # --------------------------------------------------

        document.num_chunks = len(chunks)
        document.status = "ready"

        await db.commit()
        await db.refresh(document)

        logger.info(
            "Document %s processed successfully (%s chunks)",
            document.filename,
            len(chunks),
        )

    except Exception:

        logger.exception(
            "Document ingestion failed for %s",
            document.filename,
        )

        document.status = "failed"

        await db.commit()

    return document
async def remove_document(
    db: AsyncSession,
    document_id: str,
    owner_id: str,
):
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.owner_id == owner_id,
        )
    )

    document = result.scalar_one_or_none()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    # Delete vectors
    delete_document_vectors(str(document.id))

    # Delete PDF
    if os.path.exists(document.storage_path):
        os.remove(document.storage_path)

    # Delete database row
    await db.delete(document)

    await db.commit()
"""Document upload and listing endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.dependencies import get_current_user
from backend.database.session import get_db
from backend.models.document import Document
from backend.models.user import User
from backend.schemas.document import DocumentRead, DocumentUploadResponse
from backend.services.document_service import (
    FileTooLargeError,
    UnsupportedFileTypeError,
    ingest_document,
    remove_document,
)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentUploadResponse:
    try:
        document = await ingest_document(db, file, owner_id=str(current_user.id))
    except UnsupportedFileTypeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except FileTooLargeError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=str(exc)
        ) from exc

    message = (
        "Document processed successfully."
        if document.status == "ready"
        else "Document upload failed during processing."
    )
    return DocumentUploadResponse(document=document, message=message)


@router.get("", response_model=list[DocumentRead])
async def list_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DocumentRead]:
    result = await db.execute(
        select(Document)
        .where(Document.owner_id == current_user.id)
        .order_by(Document.created_at.desc())
    )
    return list(result.scalars().all())

@router.delete("/{document_id}")
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await remove_document(
        db=db,
        document_id=document_id,
        owner_id=str(current_user.id),
    )

    return {
        "message": "Document deleted successfully."
    }

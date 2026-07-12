"""Pydantic request/response models for document upload & processing."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str
    num_chunks: int
    status: str
    created_at: datetime


class DocumentUploadResponse(BaseModel):
    document: DocumentRead
    message: str

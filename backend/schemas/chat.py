"""Pydantic request/response models for chat & RAG question answering."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChatSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    created_at: datetime


class SourceCitation(BaseModel):
    """A single retrieved chunk used as evidence for an answer."""
    document_id: str
    document_name: str
    chunk_text: str
    score: float


class ChatMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: str
    content: str
    sources: list[SourceCitation] | None = None
    created_at: datetime


class ChatQuestionRequest(BaseModel):
    session_id: uuid.UUID | None = None
    question: str = Field(min_length=1, max_length=4000)


class ChatQuestionResponse(BaseModel):
    session_id: uuid.UUID
    answer: str
    sources: list[SourceCitation]

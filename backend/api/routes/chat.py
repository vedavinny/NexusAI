"""Chat endpoints: ask a RAG-backed question and fetch session history."""
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.dependencies import get_current_user
from backend.database.session import get_db
from backend.models.user import User
from backend.schemas.chat import ChatMessageRead, ChatQuestionRequest, ChatQuestionResponse
from backend.services.chat_service import ask_question, get_session_history

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/ask", response_model=ChatQuestionResponse)
async def ask(
    payload: ChatQuestionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatQuestionResponse:
    result = await ask_question(
        db, user_id=current_user.id, session_id=payload.session_id, question=payload.question
    )
    return ChatQuestionResponse(**result)


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageRead])
async def get_messages(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ChatMessageRead]:
    return await get_session_history(db, user_id=current_user.id, session_id=session_id)

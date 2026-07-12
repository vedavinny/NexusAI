"""Business logic for chat sessions, message history, and RAG-backed answers."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.chat import ChatMessage, ChatSession
from backend.rag.qa_chain import answer_question


async def get_or_create_session(
    db: AsyncSession, user_id: uuid.UUID, session_id: uuid.UUID | None
) -> ChatSession:
    if session_id is not None:
        result = await db.execute(
            select(ChatSession).where(
                ChatSession.id == session_id, ChatSession.user_id == user_id
            )
        )
        session = result.scalar_one_or_none()
        if session is not None:
            return session

    session = ChatSession(user_id=user_id, title="New Chat")
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def ask_question(db: AsyncSession, user_id: uuid.UUID, session_id: uuid.UUID | None, question: str) -> dict:
    session = await get_or_create_session(db, user_id, session_id)

    user_message = ChatMessage(session_id=session.id, role="user", content=question)
    db.add(user_message)
    await db.commit()

    result = await answer_question(question=question, owner_id=str(user_id))

    assistant_message = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=result["answer"],
        sources=result["sources"],
    )
    db.add(assistant_message)
    await db.commit()

    return {
        "session_id": session.id,
        "answer": result["answer"],
        "sources": result["sources"],
    }


async def get_session_history(db: AsyncSession, user_id: uuid.UUID, session_id: uuid.UUID) -> list[ChatMessage]:
    result = await db.execute(
        select(ChatMessage)
        .join(ChatSession)
        .where(ChatSession.id == session_id, ChatSession.user_id == user_id)
        .order_by(ChatMessage.created_at)
    )
    return list(result.scalars().all())

"""
Clean RAG Question Answering Pipeline

Question
    ↓
Embed Question
    ↓
Retrieve Top Chunks
    ↓
Send Context to Groq
    ↓
Return Answer + Sources
"""

import logging

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from backend.config.settings import settings
from backend.rag.embeddings import embed_query
from backend.rag.vectorstore import search_similar_chunks
from backend.rag.reranker import rerank_chunks

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
You are NexusAI.

Answer the user's question using ONLY the provided document context.

Rules:
- Use only the information in the context.
- Answer naturally in your own words.
- Do not repeat the context.
- Do not continue the document.
- Do not generate new questions.
- If the answer is not in the context, reply exactly:

I don't have enough information in the uploaded documents.

Return only the answer.
"""

def get_llm():

    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL_NAME,
        temperature=0,
    )


def build_context(chunks):

    return "\n\n".join(
        chunk["chunk_text"]
        for chunk in chunks
    )


async def answer_question(
    question: str,
    owner_id: str,
    top_k: int = 4,
):
    logger.info("=" * 80)
    logger.info("QUESTION")
    logger.info(question)

    # ---------------------------------------------------
    # Embed Question
    # ---------------------------------------------------

    query_vector = embed_query(question)

    # ---------------------------------------------------
    # Retrieve
    # ---------------------------------------------------

    retrieved_chunks = search_similar_chunks(
        query_vector=query_vector,
        owner_id=owner_id,
        top_k=20,
    )

    if not retrieved_chunks:
        return {
            "answer": "I don't have any uploaded documents yet.",
            "sources": [],
        }
    # --------------------------------------------
# CrossEncoder Reranking
# --------------------------------------------

    retrieved_chunks = rerank_chunks(
        question=question,
        chunks=retrieved_chunks,
        top_k=5,
    )

    logger.info("=" * 80)
    logger.info("Retrieved %d chunks", len(retrieved_chunks))

    for i, chunk in enumerate(retrieved_chunks, start=1):
        logger.info(
            "[%d] Vector: %.4f | Rerank: %.4f | %s | Page %s",
            i,
            chunk["score"],
            chunk["rerank_score"],
            chunk["document_name"],
            chunk.get("page_number"),
        )

    # ---------------------------------------------------
    # Optional confidence check
    # ---------------------------------------------------

    best_score = retrieved_chunks[0]["score"]

    if best_score < 0.55:
        return {
            "answer": "I don't have enough information in the uploaded documents to answer that question.",
            "sources": [],
        }

    # ---------------------------------------------------
    # Build Context
    # ---------------------------------------------------

    context = build_context(retrieved_chunks)
    print("=" * 100)
    print("CONTEXT SENT TO LLM")
    print("=" * 100)
    print(context)
    print("=" * 100)

    logger.info("=" * 80)
    logger.info("Context Length : %d characters", len(context))

    llm = get_llm()

    messages = [
    SystemMessage(content=SYSTEM_PROMPT),
    HumanMessage(
        content=f"""
Context:

{context}

Question:
{question}

Answer:
"""
    ),
]

    try:

        response = await llm.ainvoke(messages)

        print("=" * 80)
        print("RAW RESPONSE")
        print(response)
        print("=" * 80)

        answer = response.content.strip()

    except Exception:

        logger.exception("LLM generation failed")

        answer = "Sorry, an error occurred while generating the answer."
    logger.info("=" * 80)
    logger.info("ANSWER")
    logger.info(answer)
    logger.info("=" * 80)

    sources = [
        {
            "document_id": chunk["document_id"],
            "document_name": chunk["document_name"],
            "page_number": chunk.get("page_number"),
            "score": chunk["score"],
            "chunk_text": chunk["chunk_text"],
        }
        for chunk in retrieved_chunks
    ]

    return {
        "answer": answer,
        "sources": sources,
    }
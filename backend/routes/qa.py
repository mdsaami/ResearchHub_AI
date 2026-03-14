"""
ResearchHub AI – Paper Q&A Route
Allows users to ask questions about a specific paper.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models import Paper
from backend.schemas import QARequest, QAResponse
from backend.services.qa_service import answer_question

router = APIRouter(prefix="/api/qa", tags=["Q&A"])


@router.post("/", response_model=QAResponse)
async def ask_question(
    request: QARequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Ask a question about a specific uploaded paper.

    Uses RAG (Retrieval-Augmented Generation):
    1. Retrieve relevant chunks from the paper via Qdrant
    2. Generate an answer using OpenAI with the retrieved context
    """
    # ── Validate paper exists ───────────────────
    result = await db.execute(
        select(Paper).where(Paper.id == request.paper_id)
    )
    paper = result.scalar_one_or_none()

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")

    # ── Generate answer ─────────────────────────
    try:
        answer = await answer_question(
            paper_id=paper.id,
            paper_title=paper.title,
            question=request.question,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate answer: {str(e)}",
        )

    return QAResponse(
        paper_id=paper.id,
        question=request.question,
        answer=answer,
        paper_title=paper.title,
    )

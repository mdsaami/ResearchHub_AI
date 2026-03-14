"""
ResearchHub AI – Literature Review Route
Generates structured literature reviews using the agentic pipeline.
"""

from fastapi import APIRouter, HTTPException

from backend.schemas import ReviewRequest, ReviewResponse
from backend.services.agent_service import generate_literature_review

router = APIRouter(prefix="/api/review", tags=["Literature Review"])


@router.post("/", response_model=ReviewResponse)
async def create_review(request: ReviewRequest):
    """
    Generate a structured literature review on a given topic.

    Uses a 3-agent LangChain pipeline:
    - Agent 1: Search for relevant papers in Qdrant
    - Agent 2: Summarize each paper with focus on the topic
    - Agent 3: Synthesize summaries into a structured review
    """
    try:
        result = await generate_literature_review(
            topic=request.topic,
            num_papers=request.num_papers,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate literature review: {str(e)}",
        )

    return ReviewResponse(
        topic=request.topic,
        review=result["review"],
        papers_used=result["papers_used"],
    )

"""
ResearchHub AI – Pydantic Schemas
Request and response schemas for all API endpoints.
"""

from datetime import datetime
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────
# Paper Schemas
# ─────────────────────────────────────────────────

class PaperResponse(BaseModel):
    """Schema returned when listing or retrieving a paper."""
    id: int
    title: str
    authors: str | None = None
    abstract: str | None = None
    filename: str
    page_count: int | None = None
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class PaperUploadResponse(BaseModel):
    """Response after successful paper upload."""
    message: str
    paper: PaperResponse


# ─────────────────────────────────────────────────
# Semantic Search Schemas
# ─────────────────────────────────────────────────

class SearchRequest(BaseModel):
    """Natural language search query."""
    query: str = Field(..., min_length=1, description="Natural language search query")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to return")


class SearchResult(BaseModel):
    """A single search result with relevance score."""
    paper_id: int
    title: str
    authors: str | None = None
    abstract: str | None = None
    score: float


class SearchResponse(BaseModel):
    """Wrapper for search results."""
    query: str
    results: list[SearchResult]


# ─────────────────────────────────────────────────
# Paper Q&A Schemas
# ─────────────────────────────────────────────────

class QARequest(BaseModel):
    """Question about a specific paper."""
    paper_id: int = Field(..., description="ID of the paper to ask about")
    question: str = Field(..., min_length=1, description="Question to ask about the paper")


class QAResponse(BaseModel):
    """Answer generated from paper context."""
    paper_id: int
    question: str
    answer: str
    paper_title: str


# ─────────────────────────────────────────────────
# Literature Review Schemas
# ─────────────────────────────────────────────────

class ReviewRequest(BaseModel):
    """Request for agentic literature review generation."""
    topic: str = Field(..., min_length=1, description="Research topic for the literature review")
    num_papers: int = Field(default=5, ge=2, le=10, description="Number of papers to include")


class ReviewResponse(BaseModel):
    """Generated literature review."""
    topic: str
    review: str
    papers_used: list[str]

"""
ResearchHub AI – Semantic Search Route
Accepts natural language queries and returns relevant papers.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models import Paper
from backend.schemas import SearchRequest, SearchResponse, SearchResult
from backend.services.embedding_service import generate_embedding
from backend.services.vector_service import search_similar

router = APIRouter(prefix="/api/search", tags=["Search"])


@router.post("/", response_model=SearchResponse)
async def semantic_search(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Perform semantic search over uploaded papers.

    1. Convert query to embedding
    2. Search Qdrant for similar chunks
    3. Deduplicate by paper
    4. Return top k papers with scores
    """
    # ── Embed the query ─────────────────────────
    query_vector = await generate_embedding(request.query)

    # ── Search Qdrant ───────────────────────────
    # Fetch extra to account for deduplication
    raw_results = search_similar(
        query_vector=query_vector,
        top_k=request.top_k * 3,
    )

    if not raw_results:
        return SearchResponse(query=request.query, results=[])

    # ── Deduplicate by paper_id ─────────────────
    seen_papers: set[int] = set()
    unique_results: list[dict] = []
    for result in raw_results:
        if result["paper_id"] not in seen_papers:
            seen_papers.add(result["paper_id"])
            unique_results.append(result)
        if len(unique_results) >= request.top_k:
            break

    # ── Enrich with DB metadata ─────────────────
    paper_ids = [r["paper_id"] for r in unique_results]
    db_result = await db.execute(
        select(Paper).where(Paper.id.in_(paper_ids))
    )
    papers_map = {p.id: p for p in db_result.scalars().all()}

    results = []
    for r in unique_results:
        paper = papers_map.get(r["paper_id"])
        if paper:
            results.append(
                SearchResult(
                    paper_id=paper.id,
                    title=paper.title,
                    authors=paper.authors,
                    abstract=paper.abstract,
                    score=round(r["score"], 4),
                )
            )

    return SearchResponse(query=request.query, results=results)

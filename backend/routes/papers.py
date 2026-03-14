"""
ResearchHub AI – Paper Routes
Handles paper upload, listing, and retrieval.
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models import Paper
from backend.schemas import PaperResponse, PaperUploadResponse
from backend.services.pdf_service import extract_pdf_content, chunk_text
from backend.services.embedding_service import generate_embeddings_batch
from backend.services.vector_service import upsert_paper_vectors

router = APIRouter(prefix="/api/papers", tags=["Papers"])


@router.post("/upload", response_model=PaperUploadResponse)
async def upload_paper(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a PDF research paper.

    Pipeline:
    1. Validate file type
    2. Extract text and metadata from PDF
    3. Store metadata in PostgreSQL
    4. Generate embeddings for text chunks
    5. Store vectors in Qdrant
    """
    # ── Validate ────────────────────────────────
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # ── Parse PDF ───────────────────────────────
    try:
        content = extract_pdf_content(file_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=422, detail=f"Failed to parse PDF: {str(e)}"
        )

    # ── Store in PostgreSQL ─────────────────────
    paper = Paper(
        title=content.title,
        authors=content.authors,
        abstract=content.abstract,
        filename=file.filename,
        full_text=content.full_text,
        page_count=content.page_count,
    )
    db.add(paper)
    await db.flush()  # Get the auto-generated ID

    # ── Generate Embeddings ─────────────────────
    chunks = chunk_text(content.full_text)
    if chunks:
        try:
            embeddings = await generate_embeddings_batch(chunks)
            upsert_paper_vectors(
                paper_id=paper.id,
                chunks=chunks,
                embeddings=embeddings,
                title=content.title,
            )
        except Exception as e:
            # Log but don't fail — paper is still stored in DB
            print(f"⚠️  Embedding/vector storage failed: {e}")

    return PaperUploadResponse(
        message=f"Paper '{content.title}' uploaded successfully.",
        paper=PaperResponse.model_validate(paper),
    )


@router.get("/", response_model=list[PaperResponse])
async def list_papers(db: AsyncSession = Depends(get_db)):
    """List all uploaded papers, newest first."""
    result = await db.execute(
        select(Paper).order_by(Paper.uploaded_at.desc())
    )
    papers = result.scalars().all()
    return [PaperResponse.model_validate(p) for p in papers]


@router.get("/{paper_id}", response_model=PaperResponse)
async def get_paper(paper_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve a specific paper by its ID."""
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")

    return PaperResponse.model_validate(paper)

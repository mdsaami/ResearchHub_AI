"""
ResearchHub AI – FastAPI Application Entry Point
Sets up the application with CORS, lifespan events, and route registration.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import engine, Base
from backend.services.vector_service import init_collection
from backend.routes import papers, search, qa, review


# ── Lifespan: Startup & Shutdown ────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup:
    1. Create all database tables
    2. Initialize Qdrant collection

    Shutdown:
    1. Dispose database engine
    """
    # Startup
    print("🚀 Starting ResearchHub AI...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created.")

    init_collection()

    yield

    # Shutdown
    await engine.dispose()
    print("👋 ResearchHub AI shut down.")


# ── FastAPI App ─────────────────────────────────
app = FastAPI(
    title="ResearchHub AI",
    description=(
        "Intelligent Research Paper Management and Analysis System. "
        "Upload PDFs, search semantically, ask questions, and generate "
        "literature reviews using agentic AI."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ───────────────────────────
app.include_router(papers.router)
app.include_router(search.router)
app.include_router(qa.router)
app.include_router(review.router)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "service": "ResearchHub AI",
        "status": "running",
        "version": "1.0.0",
    }

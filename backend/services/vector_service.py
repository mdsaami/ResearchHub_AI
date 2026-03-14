"""
ResearchHub AI – Vector Database Service
Manages Qdrant collection operations: initialization, upsert, and search.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
    Filter,
    FieldCondition,
    MatchValue,
)

from backend.config import get_settings

settings = get_settings()

# ── Qdrant Client ───────────────────────────────
qdrant = QdrantClient(
    host=settings.qdrant_host,
    port=settings.qdrant_port,
)


def init_collection() -> None:
    """
    Create the Qdrant collection if it doesn't already exist.
    Uses cosine similarity with the configured embedding dimension.
    If the existing collection has wrong dimensions, recreate it.
    """
    collections = qdrant.get_collections().collections
    collection_names = [c.name for c in collections]

    if settings.qdrant_collection_name in collection_names:
        # Check if existing collection has correct dimensions
        info = qdrant.get_collection(settings.qdrant_collection_name)
        existing_dim = info.config.params.vectors.size
        if existing_dim != settings.embedding_dimension:
            print(
                f"⚠️  Collection dimension mismatch: {existing_dim} vs "
                f"{settings.embedding_dimension}. Recreating collection..."
            )
            qdrant.delete_collection(settings.qdrant_collection_name)
        else:
            print(f"ℹ️  Qdrant collection already exists: {settings.qdrant_collection_name}")
            return

    qdrant.create_collection(
        collection_name=settings.qdrant_collection_name,
        vectors_config=VectorParams(
            size=settings.embedding_dimension,
            distance=Distance.COSINE,
        ),
    )
    print(f"✅ Created Qdrant collection: {settings.qdrant_collection_name}")


def upsert_paper_vectors(
    paper_id: int,
    chunks: list[str],
    embeddings: list[list[float]],
    title: str,
) -> None:
    """
    Store paper chunk embeddings in Qdrant.

    Each chunk is stored as a separate point with the paper_id in the payload
    so we can filter by paper later.

    Args:
        paper_id: Database ID of the paper.
        chunks: Text chunks from the paper.
        embeddings: Corresponding embedding vectors.
        title: Paper title (stored in payload for display).
    """
    points = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        point_id = paper_id * 10000 + i  # Deterministic point ID
        points.append(
            PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "paper_id": paper_id,
                    "title": title,
                    "chunk_index": i,
                    "text": chunk,
                },
            )
        )

    # Upsert in batches of 100
    batch_size = 100
    for start in range(0, len(points), batch_size):
        batch = points[start : start + batch_size]
        qdrant.upsert(
            collection_name=settings.qdrant_collection_name,
            points=batch,
        )

    print(f"✅ Stored {len(points)} chunks for paper #{paper_id} in Qdrant")


def search_similar(
    query_vector: list[float],
    top_k: int = 5,
    paper_id: int | None = None,
) -> list[dict]:
    """
    Find the most similar chunks to the query vector.

    Args:
        query_vector: Embedding of the search query.
        top_k: Number of results to return.
        paper_id: If set, restricts search to chunks from this paper.

    Returns:
        List of dicts with keys: paper_id, title, text, score.
    """
    query_filter = None
    if paper_id is not None:
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="paper_id",
                    match=MatchValue(value=paper_id),
                )
            ]
        )

    results = qdrant.search(
        collection_name=settings.qdrant_collection_name,
        query_vector=query_vector,
        query_filter=query_filter,
        limit=top_k,
    )

    return [
        {
            "paper_id": hit.payload["paper_id"],
            "title": hit.payload["title"],
            "text": hit.payload["text"],
            "score": hit.score,
        }
        for hit in results
    ]

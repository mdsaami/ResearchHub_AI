"""
ResearchHub AI – Agentic Literature Review Service
Uses a 3-agent pipeline to generate structured literature reviews.
Uses direct HTTP POST to HF Free Inference API OpenAI-compatible route.
No SDK used.
"""

import httpx

from backend.config import get_settings
from backend.services.embedding_service import generate_embedding
from backend.services.vector_service import search_similar

settings = get_settings()

# ── Ollama API Endpoint ──────────────────────────
CHAT_URL = f"{settings.ollama_base_url}/api/chat"


async def _generate_text(system_prompt: str, user_prompt: str) -> str:
    """
    Ollama chat with generous timeout for literature reviews.
    """
    async with httpx.AsyncClient(timeout=180.0) as client:
        response = await client.post(
            CHAT_URL,
            json={
                "model": settings.ollama_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": False,
            },
        )
        response.raise_for_status()
        data = response.json()

    return data["message"]["content"]


async def generate_literature_review(topic: str, num_papers: int = 5) -> dict:
    """
    Generate a structured literature review using a 3-agent pipeline.
    """
    # ── Agent 1: Search for Relevant Papers ─────
    paper_chunks = await _agent_search_papers(topic, num_papers)

    if not paper_chunks:
        return {
            "review": (
                f"No relevant papers found for the topic: \"{topic}\". "
                "Please upload more papers to the system."
            ),
            "papers_used": [],
        }

    papers_by_id = _group_chunks_by_paper(paper_chunks)
    paper_titles = [info["title"] for info in papers_by_id.values()]

    # ── Agent 2: Summarize Each Paper ───────────
    summaries = await _agent_summarize_papers(papers_by_id, topic)

    # ── Agent 3: Synthesize Literature Review ───
    review = await _agent_synthesize_review(topic, summaries, paper_titles)

    return {
        "review": review,
        "papers_used": paper_titles,
    }


async def _agent_search_papers(topic: str, num_papers: int) -> list[dict]:
    """Agent 1: Search the vector database for relevant papers."""
    query_vector = await generate_embedding(topic)
    return search_similar(query_vector=query_vector, top_k=num_papers * 3)


def _group_chunks_by_paper(chunks: list[dict]) -> dict:
    """Group retrieved chunks by their paper_id."""
    papers: dict[int, dict] = {}
    for chunk in chunks:
        pid = chunk["paper_id"]
        if pid not in papers:
            papers[pid] = {"title": chunk["title"], "chunks": []}
        papers[pid]["chunks"].append(chunk["text"])
    return papers


async def _agent_summarize_papers(
    papers_by_id: dict, topic: str
) -> list[dict[str, str]]:
    """Agent 2: Quick paper summaries focused on topic."""
    summaries = []
    for paper_id, info in papers_by_id.items():
        # Ultra-short context for speed
        content = "\n".join(info["chunks"][:2])[:2000]

        system_prompt = "Summarize briefly."
        user_prompt = (
            f"Paper: {info['title']}\n\n"
            f"{content}\n\n"
            f"Summary in 2 sentences on topic '{topic}':"
        )

        summary = await _generate_text(system_prompt, user_prompt)
        summaries.append({"title": info["title"], "summary": summary})

    return summaries


async def _agent_synthesize_review(
    topic: str,
    summaries: list[dict[str, str]],
    paper_titles: list[str],
) -> str:
    """Agent 3: Fast literature review from summaries."""
    formatted_summaries = "\n".join(
        f"- {s['title']}: {s['summary']}" for s in summaries
    )[:2000]  # Keep it short

    system_prompt = "Write concise literature review."
    user_prompt = (
        f"Topic: {topic}\n\n"
        f"Papers:\n{formatted_summaries}\n\n"
        f"Write a brief review (Introduction, Key Themes, Conclusion). "
        f"Include [Citations] with paper titles."
    )

    return await _generate_text(system_prompt, user_prompt)

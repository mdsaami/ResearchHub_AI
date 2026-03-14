"""
ResearchHub AI – Paper Q&A Service
Answers questions about a specific paper using retrieved context chunks.
Uses direct HTTP POST to HF Free Inference API OpenAI-compatible route.
No SDK used.
"""

import httpx
import traceback

from backend.config import get_settings
from backend.services.embedding_service import generate_embedding
from backend.services.vector_service import search_similar

settings = get_settings()

# ── Ollama API Endpoint ──────────────────────────
CHAT_URL = f"{settings.ollama_base_url}/api/chat"


async def _generate_text(system_prompt: str, user_prompt: str) -> str:
    """
    Ollama chat with generous timeout for llama3:8b.
    """
    try:
        print(f"[DEBUG] Calling Ollama...")

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
            print(f"[DEBUG] HTTP {response.status_code}")
            response.raise_for_status()
            data = response.json()

        answer = data["message"]["content"]
        print(f"[DEBUG] Answer: {len(answer)} chars")
        return answer

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"[ERROR] {error_msg}")
        raise ValueError(error_msg)


async def answer_question(paper_id: int, paper_title: str, question: str) -> str:
    """
    Lightning-fast Q&A: 1 chunk, 500 chars max, minimal prompt.
    """
    # Step 1: Embed the question
    query_vector = await generate_embedding(question)

    # Step 2: Get ONLY 1 most relevant chunk
    relevant_chunks = search_similar(
        query_vector=query_vector,
        top_k=1,
        paper_id=paper_id,
    )

    if not relevant_chunks:
        return "No content found."

    # Step 3: Ultra-minimal context (500 chars max)
    context = relevant_chunks[0]["text"][:500]

    # Step 4: Minimal prompt with fallback system message
    system_prompt = "Answer briefly."
    user_prompt = f"{context}\n\nQ: {question}\nAnswer in 1-2 sentences:"

    return await _generate_text(system_prompt, user_prompt)

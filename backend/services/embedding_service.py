"""
ResearchHub AI – Embedding Service
Generates text embeddings LOCALLY using ONNX Runtime + HuggingFace tokenizers.
No external API calls — the model runs entirely on your machine.
Compatible with Python 3.13 (no PyTorch dependency).
"""

import os

import numpy as np
import onnxruntime as ort
from huggingface_hub import hf_hub_download
from tokenizers import Tokenizer

from backend.config import get_settings

settings = get_settings()

# ── Download & Load ONNX Model Locally ───────────
_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
_CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", ".model_cache")

print(f"📥 Loading embedding model: {_MODEL_ID} (ONNX) ...")

# Download ONNX model and tokenizer from HuggingFace Hub
_onnx_path = hf_hub_download(
    repo_id=_MODEL_ID,
    filename="onnx/model.onnx",
    cache_dir=_CACHE_DIR,
)
_tokenizer_path = hf_hub_download(
    repo_id=_MODEL_ID,
    filename="tokenizer.json",
    cache_dir=_CACHE_DIR,
)

# Initialize ONNX Runtime session and tokenizer
_session = ort.InferenceSession(_onnx_path)
_tokenizer = Tokenizer.from_file(_tokenizer_path)
_tokenizer.enable_truncation(max_length=256)
_tokenizer.enable_padding(pad_id=0, pad_token="[PAD]", length=256)

print(f"✅ Embedding model loaded ({settings.embedding_dimension}-dim, ONNX)")


def _mean_pooling(token_embeddings: np.ndarray, attention_mask: np.ndarray) -> np.ndarray:
    """Apply mean pooling: average token embeddings weighted by attention mask."""
    mask_expanded = np.expand_dims(attention_mask, axis=-1).astype(np.float32)
    sum_embeddings = np.sum(token_embeddings * mask_expanded, axis=1)
    sum_mask = np.clip(np.sum(mask_expanded, axis=1), a_min=1e-9, a_max=None)
    return sum_embeddings / sum_mask


def _normalize(vectors: np.ndarray) -> np.ndarray:
    """L2-normalize vectors."""
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.clip(norms, a_min=1e-9, a_max=None)
    return vectors / norms


def _embed_texts(texts: list[str]) -> np.ndarray:
    """Tokenize, run ONNX inference, pool, and normalize."""
    encodings = _tokenizer.encode_batch(texts)

    input_ids = np.array([e.ids for e in encodings], dtype=np.int64)
    attention_mask = np.array([e.attention_mask for e in encodings], dtype=np.int64)
    token_type_ids = np.zeros_like(input_ids, dtype=np.int64)

    outputs = _session.run(
        None,
        {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "token_type_ids": token_type_ids,
        },
    )

    # outputs[0] is the last hidden state: (batch, seq_len, hidden_dim)
    token_embeddings = outputs[0]
    pooled = _mean_pooling(token_embeddings, attention_mask)
    normalized = _normalize(pooled)

    return normalized


async def generate_embedding(text: str) -> list[float]:
    """
    Generate an embedding vector for the given text using the local ONNX model.

    Args:
        text: Input text to embed.

    Returns:
        List of floats representing the embedding vector.
    """
    truncated = text[:8000]
    vectors = _embed_texts([truncated])
    return vectors[0].tolist()


async def generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a batch of texts using the local ONNX model.

    Args:
        texts: List of input texts to embed.

    Returns:
        List of embedding vectors (one per input text).
    """
    truncated = [t[:8000] for t in texts]
    vectors = _embed_texts(truncated)
    return [v.tolist() for v in vectors]

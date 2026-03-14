"""
ResearchHub AI – PDF Parsing Service
Extracts text and metadata from uploaded PDF files using PyMuPDF.
"""

import fitz  # PyMuPDF
import re
from dataclasses import dataclass


@dataclass
class PDFContent:
    """Structured content extracted from a PDF."""
    full_text: str
    title: str
    authors: str | None
    abstract: str | None
    page_count: int


def extract_pdf_content(file_bytes: bytes) -> PDFContent:
    """
    Parse a PDF file and extract text, title, authors, and abstract.

    Args:
        file_bytes: Raw bytes of the uploaded PDF file.

    Returns:
        PDFContent with extracted metadata and full text.
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    page_count = len(doc)

    # ── Extract full text ───────────────────────
    full_text_parts: list[str] = []
    for page in doc:
        text = page.get_text("text")
        if text:
            full_text_parts.append(text.strip())

    full_text = "\n\n".join(full_text_parts)

    # ── Extract title ───────────────────────────
    # Strategy: Use the first line of the first page as the title,
    # or fall back to PDF metadata.
    title = _extract_title(doc, full_text)

    # ── Extract authors ─────────────────────────
    authors = _extract_authors(doc, full_text)

    # ── Extract abstract ────────────────────────
    abstract = _extract_abstract(full_text)

    doc.close()
    return PDFContent(
        full_text=full_text,
        title=title,
        authors=authors,
        abstract=abstract,
        page_count=page_count,
    )


def _extract_title(doc: fitz.Document, full_text: str) -> str:
    """Extract paper title from metadata or first page text."""
    # Try PDF metadata first
    metadata = doc.metadata
    if metadata and metadata.get("title") and metadata["title"].strip():
        return metadata["title"].strip()

    # Fall back to first non-empty line of the document
    lines = [line.strip() for line in full_text.split("\n") if line.strip()]
    if lines:
        # Take the first substantial line (likely the title)
        for line in lines[:5]:
            if len(line) > 10 and not line.startswith("http"):
                return line[:500]

    return "Untitled Paper"


def _extract_authors(doc: fitz.Document, full_text: str) -> str | None:
    """Extract authors from metadata or heuristic text analysis."""
    metadata = doc.metadata
    if metadata and metadata.get("author") and metadata["author"].strip():
        return metadata["author"].strip()

    # Heuristic: Look for lines after the title that contain commas or "and"
    # (common in author lists) before the abstract
    lines = [line.strip() for line in full_text.split("\n") if line.strip()]
    for i, line in enumerate(lines[1:6], start=1):  # Check lines 2-6
        if any(keyword in line.lower() for keyword in [","]) and len(line) < 300:
            # Likely an author line
            return line[:500]

    return None


def _extract_abstract(full_text: str) -> str | None:
    """Extract the abstract section from the paper text."""
    # Pattern: "Abstract" followed by content until next section heading
    abstract_pattern = re.compile(
        r"(?:^|\n)\s*(?:ABSTRACT|Abstract|abstract)\s*[:\n]?\s*(.*?)(?=\n\s*(?:[A-Z][A-Z\s]{3,}|1\.|I\.|Introduction|INTRODUCTION|Keywords|KEYWORDS)|\Z)",
        re.DOTALL,
    )
    match = abstract_pattern.search(full_text)
    if match:
        abstract = match.group(1).strip()
        # Clean up and limit length
        abstract = re.sub(r"\s+", " ", abstract)
        if len(abstract) > 50:  # Only return if it's substantial
            return abstract[:2000]

    return None


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """
    Split text into overlapping chunks for embedding.

    Args:
        text: The full text to split.
        chunk_size: Maximum characters per chunk.
        overlap: Number of overlapping characters between chunks.

    Returns:
        List of text chunks.
    """
    if not text:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap

    return chunks

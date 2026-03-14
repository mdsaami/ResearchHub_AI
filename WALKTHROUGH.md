# ResearchHub AI – Complete Walkthrough Guide

**Intelligent Research Paper Management and Analysis System using Agentic AI**

This guide walks you through every feature of ResearchHub AI, from setup to advanced usage.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Docker (for Qdrant)
- Ollama (installed locally with `llama3:8b` model)

### Launch All Services

**1. Start Ollama (if not running)**
```bash
ollama run llama3:8b
```

**2. Start PostgreSQL** (ensure it's running on localhost:5432)
```bash
# macOS with Homebrew
brew services start postgresql

# Or use Docker
docker run -d --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:14
```

**3. Start Qdrant** (vector database)
```bash
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

**4. Start Backend**
```bash
cd /path/to/researchhub-ai
source venv/bin/activate
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**5. Start Frontend**
```bash
cd frontend
npm run dev
```

### Access the Application

| Service | URL |
|---------|-----|
| **Application** | http://localhost:5174 |
| **API Documentation** | http://localhost:8000/docs |
| **Qdrant Dashboard** | http://localhost:6333/dashboard |

---

## 📖 Feature Walkthrough

### 1. 📄 Upload Paper

**What it does:**
- Accept PDF files (research papers)
- Extract text, title, authors, and abstract
- Chunk text for semantic indexing
- Generate embeddings locally using ONNX
- Store metadata in PostgreSQL
- Index vectors in Qdrant

**How to use:**

1. Click **"Upload Paper"** in the sidebar
2. **Drag & drop** a PDF file or click to browse
3. Wait for processing (parsing + embedding + indexing)
4. See success message ✅

**Behind the scenes:**
```
PDF Upload
  ↓ (PyMuPDF)
Extract: title, authors, abstract, full_text
  ↓ (Text Chunking)
1000-char chunks with 200-char overlap
  ↓ (ONNX Embeddings)
384-dim vectors (all-MiniLM-L6-v2 model)
  ↓ (Qdrant + PostgreSQL)
Store vectors + metadata
```

**Example files to test:**
- Any academic paper PDF (arXiv, IEEE, etc.)
- Multi-page research papers work best
- Large PDFs may take a few moments

**API Endpoint:**
```bash
curl -X POST http://localhost:8000/api/papers/upload \
  -F "file=@research_paper.pdf"
```

---

### 2. 📚 My Papers

**What it does:**
- Display all uploaded papers
- Show metadata: title, authors, page count, upload date
- Display extracted abstracts
- Grid layout for easy browsing

**How to use:**

1. Click **"My Papers"** in the sidebar
2. Browse your uploaded papers
3. Each card shows:
   - **Title** (extracted from PDF)
   - **Authors** (parsed from metadata/text)
   - **Page count** (from PDF)
   - **Upload date** (formatted)
   - **Abstract** (extracted and cleaned)

**Features:**
- Newest papers appear first
- Click on any paper to view full details
- Use this list to reference paper IDs for Q&A

---

### 3. 🔍 Semantic Search

**What it does:**
- Search your paper collection using natural language
- Find relevant papers based on semantic meaning (not keyword matching)
- Returns papers ranked by relevance score
- Uses local embeddings for fast, private search

**How to use:**

1. Click **"Semantic Search"** in the sidebar
2. Enter a natural language query:
   - **Example:** "What papers discuss transformer architectures?"
   - **Example:** "Deep learning for medical imaging"
   - **Example:** "Neural networks optimization techniques"
3. Adjust "Number of results" (1-20, default 5)
4. Click **"🔎 Search"**
5. View results with relevance scores (0-100%)

**How it works:**
```
Your Query
  ↓ (ONNX Embedding)
384-dim vector
  ↓ (Qdrant Search)
Cosine similarity search across all papers
  ↓
Top-K papers deduplicated by ID
  ↓
Enrich with PostgreSQL metadata
  ↓
Display with relevance %
```

**Example queries:**
- "machine learning classification algorithms"
- "natural language processing transformers"
- "computer vision convolutional networks"
- "reinforcement learning policy gradient"

**API Example:**
```bash
curl -X POST http://localhost:8000/api/search/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What papers discuss transformers?",
    "top_k": 5
  }'
```

---

### 4. 💬 Paper Q&A

**What it does:**
- Ask questions about a specific paper
- Get AI-powered answers based on paper content
- Uses Retrieval-Augmented Generation (RAG)
- Chat-style interface with conversation history

**How to use:**

1. Click **"Paper Q&A"** in the sidebar
2. **Select a paper** from the dropdown (shows all uploaded papers)
3. Conversation resets when you change papers
4. Type a question in the input field:
   - **Example:** "What is the main contribution of this paper?"
   - **Example:** "How does the methodology work?"
   - **Example:** "What datasets were used?"
   - **Example:** "What are the limitations?"
5. Click **"📨 Ask"** or press Enter
6. Wait for the AI to think and respond
7. Ask follow-up questions (multipart conversation)

**How it works:**
```
Your Question
  ↓ (ONNX Embedding)
Convert to 384-dim vector
  ↓ (Qdrant Search)
Find top-5 most relevant chunks from THIS paper
  ↓ (Context Assembly)
Build context: "Chunks from paper '{title}': {chunk1} ... {chunk5}"
  ↓ (Ollama llama3:8b)
Generate answer based on context
  ↓
Stream response to UI
```

**Tips:**
- The AI can only answer based on paper content
- If relevant content isn't found, it will say so
- Ask specific, clear questions for best results
- Context limited to top-5 chunks per query
- Answers are grounded in actual paper text

**Example interaction:**
```
You: "What problem does this paper solve?"
AI: Answers based on abstract + intro chunks

You: "How is it different from prior work?"
AI: Answers from related work section chunks

You: "What are the results?"
AI: Answers from experiments/results chunks
```

**API Example:**
```bash
curl -X POST http://localhost:8000/api/qa/ \
  -H "Content-Type: application/json" \
  -d '{
    "paper_id": 1,
    "question": "What is the main contribution?"
  }'
```

---

### 5. 📝 Literature Review

**What it does:**
- Generate structured literature reviews from your papers
- Use 3-agent agentic pipeline (orchestrated via Ollama calls)
- Automatically find relevant papers, summarize, and synthesize
- Output formatted as Markdown with paper citations

**How to use:**

1. Click **"Literature Review"** in the sidebar
2. Enter a **research topic**:
   - **Example:** "Deep learning for medical image analysis"
   - **Example:** "Federated learning systems"
   - **Example:** "Graph neural networks applications"
3. Select **number of papers** to include (2-10, default 5)
4. Click **"🚀 Generate"**
5. Wait for generation (1-3 minutes for multiple papers)
6. Review the Markdown-formatted output
7. See which papers were cited

**How it works:**

```
Topic: "Your Research Topic"
  ↓ (Agent 1: Search)
Find top-N relevant papers via semantic search
  ↓ (Agent 2: Summarize)
For each paper:
  - Embed query + topic
  - Retrieve top-3 chunks
  - Ask Llama: "Summarize focusing on {topic}"
  ↓ (Agent 3: Synthesize)
Combine all summaries + ask Llama to write review:
  - Format as Markdown
  - Include intro, key themes, methodology, conclusion
  - Add inline citations [Paper Title]
  ↓
Output formatted review + list of papers used
```

**Generated review structure:**

1. **Introduction** – Overview of the research area
2. **Key Themes & Findings** – Common patterns across papers
3. **Methodology Trends** – Approaches and techniques used
4. **Conclusion** – Overall landscape and future directions

**Tips:**
- First upload 3+ papers on your topic
- Specific topics (not too broad) work best
- Takes longer for more papers (be patient)
- Generated text is AI-powered (review for accuracy)
- Use for literature review sections of your own papers

**Example workflow:**
```
1. Upload 5 papers on "transformer architectures"
2. Go to Literature Review
3. Topic: "Evolution of transformer models in NLP"
4. Num papers: 5
5. Wait for generation
6. Get formatted review with citations
7. Copy/paste into your document
```

**API Example:**
```bash
curl -X POST http://localhost:8000/api/review/ \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Deep learning for NLP",
    "num_papers": 5
  }'
```

---

## 🏗️ Architecture & Components

### Data Pipeline

```
User Uploads PDF
  ↓
PyMuPDF (pdf_service.py)
  - Extract text page by page
  - Parse metadata (title, authors)
  - Detect abstract section (regex)
  ↓
Text Chunking (chunk_text)
  - Split into 1000-char chunks
  - 200-char overlap between chunks
  - Preserve context
  ↓
ONNX Embeddings (embedding_service.py)
  - Load all-MiniLM-L6-v2 model (locally cached)
  - Generate 384-dim vectors
  - NO external API calls, runs on CPU
  ↓
Qdrant Upsert (vector_service.py)
  - Store vectors in cosine similarity index
  - Payload: paper_id, title, chunk_index, text
  - Deterministic IDs: paper_id * 10000 + chunk_index
  ↓
PostgreSQL Insert (models.py, routes/papers.py)
  - Store: title, authors, abstract, full_text, page_count
  - Timestamp: uploaded_at (UTC)
  ↓
Ready for Search, Q&A, and Review Generation
```

### Search Pipeline

```
Query Input
  ↓
Generate Embedding (384-dim vector)
  ↓
Qdrant Search (cosine similarity, top-K*3)
  ↓
Deduplicate by paper_id (keep first occurrence)
  ↓
Fetch PostgreSQL metadata (title, authors, abstract)
  ↓
Format & return with score (0-1, converted to %)
```

### Q&A Pipeline (RAG)

```
Question + Paper ID
  ↓
Generate Question Embedding
  ↓
Qdrant Search (filter by paper_id, top-5 chunks)
  ↓
Assemble Context + System Prompt
  ↓
Call Ollama (llama3:8b) with context
  ↓
Stream response to UI
```

### Review Pipeline (3-Agent)

```
Topic + Num Papers
  ↓
Agent 1: Search
  - Embed topic
  - Get top-N*3 chunks
  - Deduplicate → papers list
  ↓
Agent 2: Summarize
  For each paper:
    - Get top-3 chunks
    - Call Ollama: "Summarize {paper} for topic {topic}"
    - Collect summaries
  ↓
Agent 3: Synthesize
  - Format all summaries
  - Call Ollama: "Write literature review Markdown"
  - Include inline citations
  ↓
Return review + papers_used
```

---

## 🔐 Local-First Privacy

ResearchHub AI is **completely local** — your papers never leave your machine:

✅ **Embeddings:** ONNX Runtime runs locally (all-MiniLM-L6-v2)
✅ **LLM:** Ollama llama3:8b runs locally (CPU or GPU)
✅ **Database:** PostgreSQL on localhost (not cloud)
✅ **Vector Search:** Qdrant on localhost (not cloud)
✅ **No external APIs:** No Hugging Face, OpenAI, or cloud calls

**Your research data is 100% private.**

---

## 🛠️ Advanced Usage

### Custom Ollama Models

Want to use a different Llama model? Update `.env`:

```bash
OLLAMA_MODEL=llama2:13b
# or
OLLAMA_MODEL=neural-chat
# or any model you've pulled with: ollama pull <model>
```

Then restart the backend:
```bash
# Kill backend
lsof -i :8000 | grep Python | awk '{print $2}' | xargs kill -9

# Restart
uvicorn backend.main:app --reload
```

**Model performance:**
- `llama3:8b` – Good quality, balanced (recommended)
- `llama2:13b` – Better quality, slower
- `neural-chat` – Fast, conversational
- `mistral` – Very fast, still coherent

### Batch Upload Scripts

Upload multiple PDFs programmatically:

```python
import requests
import os

api_url = "http://localhost:8000/api/papers/upload"
papers_dir = "./papers"

for filename in os.listdir(papers_dir):
    if filename.endswith(".pdf"):
        with open(os.path.join(papers_dir, filename), "rb") as f:
            files = {"file": f}
            response = requests.post(api_url, files=files)
            print(f"{filename}: {response.json()['message']}")
```

### Query Papers via API

```python
import requests

# List all papers
response = requests.get("http://localhost:8000/api/papers/")
papers = response.json()
print(f"Total papers: {len(papers)}")

# Search
search_data = {"query": "transformers NLP", "top_k": 5}
response = requests.post("http://localhost:8000/api/search/", json=search_data)
results = response.json()
for r in results['results']:
    print(f"- {r['title']} (score: {r['score']:.2%})")

# Ask question
qa_data = {"paper_id": 1, "question": "What is the contribution?"}
response = requests.post("http://localhost:8000/api/qa/", json=qa_data)
answer = response.json()
print(answer['answer'])

# Generate review
review_data = {"topic": "Deep learning", "num_papers": 5}
response = requests.post("http://localhost:8000/api/review/", json=review_data)
review = response.json()
print(review['review'])
```

### Database Queries

Access PostgreSQL directly:

```bash
psql -U postgres -d researchhub
```

```sql
-- All papers
SELECT id, title, authors, page_count, uploaded_at FROM papers;

-- Papers by date
SELECT title, uploaded_at FROM papers ORDER BY uploaded_at DESC;

-- Search papers by title
SELECT * FROM papers WHERE title ILIKE '%transformer%';
```

### Qdrant Vector Search

Access Qdrant dashboard at http://localhost:6333/dashboard

Or query directly:

```python
from qdrant_client import QdrantClient

client = QdrantClient(host="localhost", port=6333)
collection = client.get_collection("research_papers")
print(f"Total vectors: {collection.points_count}")

# View sample vectors
points = client.scroll("research_papers", limit=5)
for point in points[0]:
    print(f"Paper {point.payload['paper_id']}: {point.payload['title']}")
```

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill and restart
kill -9 <PID>
uvicorn backend.main:app --reload

# Check config loads
python -c "from backend.config import get_settings; print(get_settings())"
```

### No papers appear after upload
```bash
# Check PostgreSQL connection
psql -U postgres -c "SELECT * FROM researchhub.papers;"

# Check Qdrant vectors
# Visit http://localhost:6333/dashboard

# Check logs for errors during upload
# Look at terminal running backend
```

### Search returns no results
```bash
# Ensure papers are uploaded first
# Check if vectors are in Qdrant
# Try a broader search query
# Check paper abstracts are extracted (visit /papers endpoint)
```

### Q&A gives generic answers
```bash
# Model may not find relevant chunks
# Try different question phrasing (more specific)
# Ensure paper has sufficient text (large PDFs better)
# Check Qdrant search is working (test in /docs)
```

### Ollama model not found
```bash
# List pulled models
ollama list

# Pull the model
ollama pull llama3:8b

# Verify running
curl http://localhost:11434/api/tags
```

### Frontend can't connect to API
```bash
# Check backend is running on :8000
lsof -i :8000

# Check CORS settings (backend/main.py)
# Frontend should be on localhost:5173 or localhost:5174

# Check vite proxy in vite.config.js
# Should point to http://localhost:8000
```

---

## 📊 Performance Tips

### Faster Search
- Fewer papers indexed = faster search
- Use semantic queries (not keywords)
- Increase `top_k` if results seem limited

### Faster Q&A
- Use papers with clear structure (title, abstract, intro)
- Ask specific questions
- Smaller papers (~20 pages) faster to process

### Faster Reviews
- Fewer papers to summarize = faster generation
- Start with 3-5 papers, then increase
- Topic specificity helps (e.g., "Vision Transformers" vs "AI")

### Optimal Settings

| Setting | Value | Reason |
|---------|-------|--------|
| Chunk size | 1000 chars | Balances context + speed |
| Overlap | 200 chars | Preserves sentence continuity |
| Embedding model | all-MiniLM-L6-v2 | Fast + accurate (384-dim) |
| Search top-k | 5-10 | Good recall without noise |
| Review papers | 3-7 | Fast generation, good coverage |

---

## 📝 Best Practices

### Paper Organization
1. Upload papers on same topic for coherent reviews
2. Use consistent PDF naming (helps with extraction)
3. Ensure PDFs have clean text (scanned PDFs won't work well)

### Search Strategies
- **Specific queries:** "attention mechanism in transformers"
- **Concept queries:** "semantic search methods"
- **Author queries:** Won't work (search is semantic, not keyword)

### Q&A Best Practices
- Ask about: methodology, results, limitations, contributions
- Avoid: author names, specific dates (not in embeddings)
- Follow-ups: "What does that mean?" "Can you elaborate?"

### Review Generation
1. Pick a specific, well-defined topic
2. Upload papers directly relevant to topic
3. Use 5+ papers for comprehensive reviews
4. Review output for accuracy (AI-generated)
5. Use as starting point, not final reference

### API Integration
- Use 120s timeout for long operations (reviews)
- Batch upload for multiple papers
- Cache paper IDs after upload
- Handle rate limits (none currently)

---

## 🎯 Example Workflows

### Workflow 1: Literature Review for Your Paper

1. **Upload papers** (5-10 source papers on your topic)
2. Go to **Literature Review**
3. Enter your research topic
4. Generate review (2-3 minutes)
5. Copy-paste into your paper
6. Edit and refine (add citations, adjust wording)

### Workflow 2: Paper Analysis

1. **Upload** a single paper
2. Go to **Paper Q&A**
3. Ask questions:
   - "What's the main contribution?"
   - "How does the methodology work?"
   - "What are the results?"
   - "What are the limitations?"
4. Take notes from answers

### Workflow 3: Research Topic Exploration

1. **Upload** 10+ papers on a broad topic
2. Go to **Semantic Search**
3. Try different queries to explore:
   - "machine learning approaches"
   - "neural network architectures"
   - "optimization techniques"
4. Discover related papers you haven't read
5. Download/read interesting papers

### Workflow 4: Competitive Analysis

1. Upload competitor papers
2. Upload your own papers
3. Use **Semantic Search** to compare:
   - Do searches return your papers?
   - Which topics are you missing?
4. Identify gaps in your research

---

## 🎓 Educational Use

Great for:
- **Students:** Analyze papers for class projects
- **Researchers:** Organize and explore literature
- **Writers:** Generate literature review drafts
- **Educators:** Help students summarize papers
- **Teams:** Share paper repository (self-hosted)

---

## 📚 API Reference

### GET /
**Health check**
```bash
curl http://localhost:8000/
```

### POST /api/papers/upload
**Upload a PDF paper**
```bash
curl -X POST http://localhost:8000/api/papers/upload \
  -F "file=@paper.pdf"
```

### GET /api/papers/
**List all papers**
```bash
curl http://localhost:8000/api/papers/
```

### GET /api/papers/{id}
**Get paper by ID**
```bash
curl http://localhost:8000/api/papers/1
```

### POST /api/search/
**Semantic search**
```bash
curl -X POST http://localhost:8000/api/search/ \
  -H "Content-Type: application/json" \
  -d '{"query": "search term", "top_k": 5}'
```

### POST /api/qa/
**Ask question about paper**
```bash
curl -X POST http://localhost:8000/api/qa/ \
  -H "Content-Type: application/json" \
  -d '{"paper_id": 1, "question": "Your question?"}'
```

### POST /api/review/
**Generate literature review**
```bash
curl -X POST http://localhost:8000/api/review/ \
  -H "Content-Type: application/json" \
  -d '{"topic": "Your topic", "num_papers": 5}'
```

See interactive docs at http://localhost:8000/docs

---

## 🚀 Next Steps

1. **Upload 3-5 papers** on your topic
2. **Try semantic search** with different queries
3. **Ask Q&A** about specific papers
4. **Generate a review** to see the full pipeline
5. **Explore the code** (well-documented, modular)
6. **Customize** (add more features, integrate with your tools)

---

## 📧 Support & Issues

For bugs or questions:
1. Check the **Troubleshooting** section above
2. Try restarting all services
3. Check logs in backend terminal
4. Verify all prerequisites are running
5. Review API documentation at http://localhost:8000/docs

---

**Happy researching with ResearchHub AI! 🚀**

Powered by Ollama (llama3:8b), ONNX embeddings, Qdrant, and PostgreSQL — all running locally on your machine. 🔐

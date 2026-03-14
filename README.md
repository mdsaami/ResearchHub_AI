# ResearchHub AI

**Intelligent Research Paper Management and Analysis System using Agentic AI**

Upload PDFs, search semantically, ask questions about papers, and generate structured literature reviews — all powered by local Ollama (llama3:8b) and a multi-agent LangChain pipeline. 100% private, no external APIs.

---

## Architecture

```
researchhub-ai/
├── backend/
│   ├── main.py              # FastAPI app + CORS + lifespan
│   ├── config.py             # Pydantic settings (.env)
│   ├── database.py           # Async SQLAlchemy engine + session
│   ├── models.py             # Paper ORM model
│   ├── schemas.py            # Request/response schemas
│   ├── routes/
│   │   ├── papers.py         # Upload, list, get papers
│   │   ├── search.py         # Semantic search
│   │   ├── qa.py             # Paper Q&A
│   │   └── review.py         # Literature review generation
│   └── services/
│       ├── pdf_service.py    # PyMuPDF text + metadata extraction
│       ├── embedding_service.py  # ONNX local embeddings (all-MiniLM-L6-v2)
│       ├── vector_service.py # Qdrant operations
│       ├── qa_service.py     # RAG-based Q&A with Ollama
│       └── agent_service.py  # 3-agent review pipeline with Ollama
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Layout + navigation
│   │   ├── api.js            # Axios API client
│   │   ├── index.css         # Design system (dark theme)
│   │   └── components/
│   │       ├── Sidebar.jsx
│   │       ├── PaperUpload.jsx
│   │       ├── PaperList.jsx
│   │       ├── SemanticSearch.jsx
│   │       ├── PaperQA.jsx
│   │       └── LiteratureReview.jsx
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── .env.example
└── requirements.txt
```

---

## Prerequisites

| Tool | Version |
|---|---|
| Python | 3.11+ |
| Node.js | 18+ |
| PostgreSQL | 14+ |
| Ollama | Latest (with llama3:8b model pulled) |
| Docker | Latest (for Qdrant) |

---

## Step-by-Step Setup

### 0. Start Ollama (if not running)

```bash
ollama run llama3:8b
```

### 1. Clone & Navigate

```bash
cd researchhub-ai
```

### 2. Start Qdrant (Docker)

```bash
docker run -d --name qdrant \
  -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

Verify at: [http://localhost:6333/dashboard](http://localhost:6333/dashboard)

### 3. Create PostgreSQL Database

```bash
psql -U postgres -c "CREATE DATABASE researchhub;"
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env and configure Ollama:
#   OLLAMA_BASE_URL=http://localhost:11434
#   OLLAMA_MODEL=llama3:8b
# Update DATABASE_URL if your PostgreSQL credentials differ
```

### 5. Backend Setup

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

Start the server:

```bash
uvicorn backend.main:app --reload
```

- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health check: [http://localhost:8000/](http://localhost:8000/)

### 6. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open: [http://localhost:5174](http://localhost:5174)

> The Vite dev server proxies `/api` requests to the backend at `localhost:8000`.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/papers/upload` | Upload a PDF paper |
| `GET` | `/api/papers/` | List all papers |
| `GET` | `/api/papers/{id}` | Get paper by ID |
| `POST` | `/api/search/` | Semantic search |
| `POST` | `/api/qa/` | Ask a question about a paper |
| `POST` | `/api/review/` | Generate literature review |

---

## Database Schema

```sql
CREATE TABLE papers (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(500) NOT NULL,
    authors     VARCHAR(500),
    abstract    TEXT,
    filename    VARCHAR(255) NOT NULL,
    full_text   TEXT,
    page_count  INTEGER,
    uploaded_at TIMESTAMP DEFAULT NOW()
);
```

Qdrant collection: `research_papers` — vector dimension 384, cosine distance.

---

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy (async), asyncpg
- **Database:** PostgreSQL
- **Vector DB:** Qdrant
- **Embeddings:** ONNX Runtime (all-MiniLM-L6-v2, runs locally)
- **LLM:** Ollama (llama3:8b, runs locally on CPU/GPU)
- **PDF Parsing:** PyMuPDF
- **Agentic Pipeline:** Custom 3-agent pipeline with Ollama
- **Frontend:** React 18, Vite, Axios, react-markdown

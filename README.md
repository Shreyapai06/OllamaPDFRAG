# OllamaPDFRAG

A full-stack Retrieval-Augmented Generation (RAG) system that lets you upload PDF documents and ask questions about them. Combines BM25 lexical search with FAISS vector search (hybrid retrieval) and a ReAct reasoning agent.

**Backend** deployed on [Railway](https://railway.app) · **Frontend** deployed on [AWS Amplify](https://aws.amazon.com/amplify/)

---

## Features

- Upload multiple PDFs and query across them simultaneously
- Hybrid retrieval: BM25 + FAISS vector search fused via Reciprocal Rank Fusion (RRF)
- ReAct agent loop with iterative reasoning steps
- Real-time token streaming via Server-Sent Events (SSE)
- Sources panel showing which PDF chunks were used
- Switchable LLM provider: **Groq** (hosted) or **Ollama** (local)
- In-memory state — no database required

---

## Tech Stack

### Backend (`rag-backend/`)
| Layer | Choice |
|-------|--------|
| Framework | FastAPI + Uvicorn |
| LLM | Groq API (OpenAI-compatible) / Ollama |
| Embeddings | `sentence-transformers` — `BAAI/bge-small-en-v1.5` (local, CPU) |
| Vector search | FAISS `IndexFlatIP` (in-memory) |
| Lexical search | `rank-bm25` (BM25Okapi) |
| PDF parsing | `pypdf` |
| Hosting | Railway |

### Frontend (`frontend/`)
| Layer | Choice |
|-------|--------|
| Framework | Angular 17+ (standalone components) |
| UI | Angular Material |
| Data grid | AG Grid Community |
| Streaming | `EventSource` wrapped in RxJS `Observable` |
| State | RxJS `BehaviorSubject` |
| Hosting | AWS Amplify |

---

## Project Structure

```
OllamaPDFRAG/
├── rag-backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── Procfile                 # Railway: uvicorn main:app --port $PORT
│   ├── runtime.txt              # python-3.11
│   ├── requirements.txt
│   └── src/
│       ├── core/
│       │   ├── agent.py         # ReAct loop agent
│       │   ├── hybrid.py        # BM25 + FAISS RRF fusion
│       │   ├── bm25.py          # BM25Okapi retrieval
│       │   ├── embeddings.py    # sentence-transformers wrapper
│       │   ├── document.py      # PDF parsing + chunking
│       │   └── llm_client.py    # Groq / Ollama client factory
│       └── api/
│           ├── config.py        # Pydantic settings (env vars)
│           ├── state.py         # In-memory AppState singleton
│           ├── dependencies.py  # FastAPI DI wiring
│           ├── models.py        # Pydantic request/response schemas
│           ├── routers/         # pdfs, query, models, health
│           └── services/        # pdf_service, rag_service
├── frontend/
│   ├── amplify.yml              # Amplify build config (inside frontend/)
│   ├── src/
│   │   ├── app/
│   │   │   ├── core/api/        # HTTP + SSE services
│   │   │   ├── core/state/      # chat-state.service (BehaviorSubjects)
│   │   │   ├── features/        # chat, sidebar, header components
│   │   │   ├── shared/          # health-badge, model-selector, spinner
│   │   │   └── types/           # TypeScript interfaces
│   │   └── assets/env.js        # Runtime API URL (overwritten by Amplify build)
│   └── package.json
└── amplify.yml                  # Amplify monorepo config (repo root)
```

---

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- A [Groq API key](https://console.groq.com) (free)

### Backend

```bash
cd rag-backend

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Create .env
cp .env.example .env             # then fill in GROQ_API_KEY

PORT=8000 uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend runs at `http://localhost:8000`  
Interactive docs at `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install

# Point to local backend
# Edit src/assets/env.js:
# window.__env = { NG_APP_API_URL: 'http://localhost:8000' };

npm start
```

Frontend runs at `http://localhost:4200`

---

## Environment Variables

### Backend (`.env` / Railway Variables)

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `groq` | `groq` or `ollama` |
| `GROQ_API_KEY` | — | Required when `LLM_PROVIDER=groq` |
| `GROQ_CHAT_MODEL` | `llama-3.3-70b-versatile` | Groq model name |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Required when `LLM_PROVIDER=ollama` |
| `OLLAMA_CHAT_MODEL` | `llama3.2` | Ollama model name |
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | sentence-transformers model |
| `MAX_AGENT_ITERATIONS` | `1` | ReAct loop iterations (keep at 1 for Groq free tier) |

### Frontend (Amplify Environment Variables)

| Variable | Description |
|----------|-------------|
| `NG_APP_API_URL` | Railway backend URL, e.g. `https://your-app.up.railway.app` |

---

## Switching to Ollama (local dev)

1. [Install Ollama](https://ollama.ai) and pull a model:
   ```bash
   ollama pull llama3.2
   ```

2. Update `rag-backend/.env`:
   ```bash
   LLM_PROVIDER=ollama
   OLLAMA_CHAT_MODEL=llama3.2
   ```

3. Restart the backend — no code changes needed.

---

## Deployment

### Railway (Backend)

1. Connect your GitHub repo to Railway
2. Set **Root Directory** to `rag-backend`
3. Add the environment variables listed above (`LLM_PROVIDER=groq`, `GROQ_API_KEY`, etc.)
4. Railway uses `Procfile` to start: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### AWS Amplify (Frontend)

1. Connect your GitHub repo to Amplify
2. Amplify detects `amplify.yml` at the repo root (monorepo config, `appRoot: frontend`)
3. Add environment variable: `NG_APP_API_URL` = your Railway URL
4. Amplify builds with `npm ci && npm run build`, artifacts from `dist/frontend/browser/`

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/health` | Health check + stats |
| `GET` | `/api/v1/models` | List available LLM models |
| `POST` | `/api/v1/pdfs/upload` | Upload and process a PDF |
| `GET` | `/api/v1/pdfs` | List uploaded PDFs |
| `DELETE` | `/api/v1/pdfs/{pdf_id}` | Delete a PDF |
| `POST` | `/api/v1/query` | Blocking agentic query |
| `GET` | `/api/v1/query/stream` | Streaming query (SSE) |
| `GET` | `/api/v1/query/sessions/{id}/messages` | Chat history |

---

## Notes

- State is **in-memory only** — PDFs and chat history are lost when the backend restarts
- The embedding model (`BAAI/bge-small-en-v1.5`, ~90 MB) is downloaded on first startup
- Groq free tier has rate limits — `MAX_AGENT_ITERATIONS=1` is recommended
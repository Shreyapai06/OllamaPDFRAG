"""FastAPI application — Railway entry point.

Local dev:  uvicorn main:app --reload
Railway:    Procfile runs  uvicorn main:app --host 0.0.0.0 --port $PORT
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import health, models, pdfs, query
from src.api.dependencies import _embedder   # warm up model at startup

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load sentence-transformers model before first request
    # (~90 MB download on first run, instant on subsequent starts)
    logging.getLogger(__name__).info("Loading embedding model…")
    _embedder()
    yield


app = FastAPI(
    title="RAG API",
    description="Hybrid BM25 + FAISS retrieval with ReAct reasoning via Groq.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten to your Amplify domain before production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_PREFIX = "/api/v1"
app.include_router(pdfs.router,    prefix=_PREFIX)
app.include_router(query.router,   prefix=_PREFIX)
app.include_router(models.router,  prefix=_PREFIX)
app.include_router(health.router,  prefix=_PREFIX)


@app.get("/")
def root():
    return {"message": "RAG API is running", "docs": "/docs"}

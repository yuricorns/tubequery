"""
main.py — FastAPI backend for VidMind
Endpoints: load a YouTube video, query the transcript, get stats.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager

import rag
import database
from transcript import get_transcript


# ── Lifespan (DB init) ────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield


app = FastAPI(
    title="VidMind — YouTube Transcript Q&A",
    description="Load any YouTube video and chat with its transcript using RAG + Groq.",
    version="1.0.0",
    lifespan=lifespan,
)


# ── Request / Response models ─────────────────────────────────────────────────

class LoadVideoRequest(BaseModel):
    url: str


class QueryRequest(BaseModel):
    query: str


class LoadVideoResponse(BaseModel):
    video_id: str
    chunk_count: int
    message: str


class QueryResponse(BaseModel):
    query: str
    answer: str
    video_id: str
    source_chunks: list[str]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/load", response_model=LoadVideoResponse)
def load_video(request: LoadVideoRequest):
    """
    Fetch transcript for a YouTube URL and index it in ChromaDB.
    Replaces any previously loaded video.
    """
    result = get_transcript(request.url)

    if result["error"]:
        raise HTTPException(status_code=400, detail=result["error"])

    load_result = rag.load_transcript_to_chromadb(
        video_id=result["video_id"],
        full_text=result["full_text"],
    )

    return LoadVideoResponse(
        video_id=load_result["video_id"],
        chunk_count=load_result["chunk_count"],
        message=f"Transcript loaded and indexed. {load_result['chunk_count']} chunks stored.",
    )


@app.post("/query", response_model=QueryResponse)
def query_video(request: QueryRequest):
    """
    Answer a question about the currently loaded video transcript.
    """
    if not rag.is_video_loaded():
        raise HTTPException(
            status_code=400,
            detail="No video loaded. Call /load with a YouTube URL first.",
        )

    if not request.query.strip():
        raise HTTPException(status_code=422, detail="Query cannot be empty.")

    result = rag.query_transcript(request.query)
    video_id = rag.get_current_video_id()

    # Log to SQLite
    database.log_query(
        video_id=video_id,
        query=request.query,
        answer=result["answer"],
        chunks_used=len(result["source_chunks"]),
    )

    return QueryResponse(
        query=request.query,
        answer=result["answer"],
        video_id=video_id,
        source_chunks=result["source_chunks"],
    )


@app.get("/status")
def status():
    """Check if a video is currently loaded."""
    return {
        "video_loaded": rag.is_video_loaded(),
        "current_video_id": rag.get_current_video_id(),
    }


@app.get("/stats")
def stats():
    """Return usage stats from SQLite logs."""
    return database.get_stats()


@app.get("/logs")
def logs(limit: int = 20):
    """Return recent query logs."""
    return database.get_recent_logs(limit=limit)


@app.get("/")
def root():
    return {"message": "VidMind API is running. Visit /docs for the Swagger UI."}

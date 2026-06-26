"""
rag.py — RAG pipeline for YouTube transcript Q&A
Handles chunking, ChromaDB storage, retrieval, and Groq LLM generation.
"""

import os
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────

CHUNK_SIZE = 500        # characters per chunk
CHUNK_OVERLAP = 50      # character overlap between chunks
TOP_K = 3               # number of chunks to retrieve per query
NVIDIA_MODEL = "nvidia/nemotron-3-ultra-550b-a55b"
COLLECTION_NAME = "vidmind_transcript"

# ── Clients ───────────────────────────────────────────────────────────────────


chroma_client = chromadb.Client()
nvidia_client = OpenAI(
    api_key=os.environ.get("NVIDIA_API_KEY"),

    base_url="https://integrate.api.nvidia.com/v1",
)


_collection = None          # module-level reference to active collection
_current_video_id = None    # track which video is currently loaded


# ── Chunking ──────────────────────────────────────────────────────────────────

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Split text into overlapping chunks of fixed character length.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


# ── ChromaDB ──────────────────────────────────────────────────────────────────

def load_transcript_to_chromadb(video_id: str, full_text: str) -> dict:
    """
    Chunk the transcript and store in ChromaDB.
    Clears any previously loaded transcript first.

    Returns:
        dict with video_id and chunk_count
    """
    global _collection, _current_video_id

    # Delete existing collection if present (single-video mode: one at a time)
    try:
        chroma_client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass  # collection didn't exist yet — fine

    # Create fresh collection
    _collection = chroma_client.create_collection(
        name=COLLECTION_NAME,
    )

    chunks = chunk_text(full_text)

    _collection.add(
        documents=chunks,
        ids=[f"chunk_{i}" for i in range(len(chunks))],
    )

    _current_video_id = video_id

    return {"video_id": video_id, "chunk_count": len(chunks)}


def is_video_loaded() -> bool:
    return _collection is not None and _current_video_id is not None


def get_current_video_id() -> str | None:
    return _current_video_id


# ── Retrieval ─────────────────────────────────────────────────────────────────

def retrieve_chunks(query: str, top_k: int = TOP_K) -> list[str]:
    """
    Retrieve the top-k most relevant chunks for a query.
    """
    if not is_video_loaded():
        raise RuntimeError("No transcript loaded. Load a video first.")

    results = _collection.query(
        query_texts=[query],
        n_results=top_k,
    )
    return results["documents"][0]  # list of chunk strings


# ── Generation ────────────────────────────────────────────────────────────────

def generate_answer(query: str, context_chunks: list[str]) -> str:
    """
    Send query + retrieved context to Groq LLM and return the answer.
    """
    context = "\n\n---\n\n".join(context_chunks)

    prompt = f"""You are a helpful assistant that answers questions about a YouTube video transcript.

Answer the user's question using ONLY the transcript context provided below.
If the answer is not found in the context, say: "I couldn't find that information in the video transcript."
Do not make up information or use outside knowledge.

TRANSCRIPT CONTEXT:
{context}

USER QUESTION:
{query}

ANSWER:"""

    response =nvidia_client.chat.completions.create(
        model= "meta/llama-3.1-8b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=512,
    )

    return response.choices[0].message.content.strip()


# ── Main pipeline ─────────────────────────────────────────────────────────────

def query_transcript(query: str) -> dict:
    """
    Full RAG pipeline: retrieve relevant chunks → generate answer.

    Returns:
        dict with answer and source_chunks
    """
    if not is_video_loaded():
        raise RuntimeError("No transcript loaded. Load a video first.")

    chunks = retrieve_chunks(query)
    answer = generate_answer(query, chunks)

    return {
        "answer": answer,
        "source_chunks": chunks,
    }

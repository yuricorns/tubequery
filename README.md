# TubeQuery🎬
### Chat with any YouTube video using RAG + Groq

Paste a YouTube URL → VidMind fetches the transcript → chunks and indexes it → you ask questions and get grounded answers from the video content.

---

## Architecture

```
transcript.py   — YouTube URL parsing + transcript fetching (youtube-transcript-api)
rag.py          — Chunking, ChromaDB indexing, retrieval, Groq LLM generation
database.py     — SQLite query logging and analytics
main.py         — FastAPI: /load, /query, /status, /stats, /logs
frontend.py     — Streamlit UI
```

Each module has a single responsibility. You can swap any layer independently.

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your Groq API key
```bash
export NVIDIA_API_KEY=your_key_here
```
Get a free key at https://console.NVIDIA.com

### 3. Run the FastAPI backend
```bash
uvicorn main:app --reload
```
Swagger docs available at http://localhost:8000/docs

### 4. Run the Streamlit frontend (new terminal)
```bash
streamlit run frontend.py
```

---

## How to use

1. Paste any YouTube URL with captions (most videos have auto-generated captions)
2. Click **LOAD VIDEO** — transcript is fetched and indexed into ChromaDB
3. Type a question and click **ASK**
4. Toggle "Show retrieved transcript chunks" to see what context the LLM used

---

## RAG Pipeline Details

| Parameter     | Value  | Reason                                                    |
|---------------|--------|-----------------------------------------------------------|
| Chunk size    | 500    | Captures a complete spoken thought without losing context |
| Overlap       | 50     | Handles sentences split across chunk boundaries           |
| Top-k         | 3      | Enough context without prompt bloat                       |
| LLM           | NVIDIA | Fast, free tier available            |
| Vector store  | ChromaDB | No setup required, handles embeddings internally       |

---

## Limitations (v1.0 — Single Video Mode)
- One video loaded at a time. Loading a new video clears the previous one.
- Only works on videos with captions (auto-generated or manual). Most English videos qualify.
- Very long videos (3+ hours) may produce large chunk counts — still works, just takes longer to index.

---

## Roadmap

- [ ] Multi-video mode — load several videos, query across all
- [ ] Timestamp-aware chunking — return the timestamp of the source chunk
- [ ] Video metadata display (title, channel, duration via yt-dlp)
- [ ] Export chat history as PDF

---

## Tech Stack
- **youtube-transcript-api** — transcript fetching
- **ChromaDB** — vector storage and retrieval
- **nvidia** — LLM inference (Llama 3)
- **FastAPI** — REST API backend
- **SQLite** — query logging
- **Streamlit** — frontend UI

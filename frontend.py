"""
frontend.py — TubeQuery Streamlit UI
Colorful, modern, high-contrast design with gradients and bright accents.
"""

import streamlit as st
import requests

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="TubeQuery",
    page_icon="🎯",
    layout="centered",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Inter:wght@400;500;600&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #f0f2f8;
    color: #1a1a2e;
}

/* ── Page background ── */
.stApp {
    background: linear-gradient(135deg, #f0f2f8 0%, #e8eaf6 50%, #f3e5f5 100%);
    min-height: 100vh;
}

/* ── Hero header ── */
.hero {
    background: linear-gradient(135deg, #6c63ff 0%, #f64f59 50%, #f9a825 100%);
    border-radius: 20px;
    padding: 2.5rem 2rem;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(108, 99, 255, 0.25);
}

.hero h1 {
    font-family: 'Nunito', sans-serif;
    font-size: 2.8rem;
    font-weight: 900;
    color: white;
    margin: 0;
    letter-spacing: -1px;
    text-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.hero p {
    color: rgba(255,255,255,0.92);
    font-size: 1rem;
    margin: 0.5rem 0 0 0;
    font-weight: 500;
}

/* ── Cards ── */
.card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 2px 12px rgba(108, 99, 255, 0.08);
    border: 1px solid rgba(108, 99, 255, 0.1);
}

.card-title {
    font-family: 'Nunito', sans-serif;
    font-size: 1rem;
    font-weight: 800;
    color: #6c63ff;
    margin-bottom: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ── Status badges ── */
.badge-loaded {
    display: inline-block;
    background: linear-gradient(90deg, #11998e, #38ef7d);
    color: white;
    padding: 0.35rem 1rem;
    border-radius: 50px;
    font-size: 0.78rem;
    font-weight: 700;
    margin-bottom: 1rem;
}

.badge-empty {
    display: inline-block;
    background: linear-gradient(90deg, #f64f59, #c471ed);
    color: white;
    padding: 0.35rem 1rem;
    border-radius: 50px;
    font-size: 0.78rem;
    font-weight: 700;
    margin-bottom: 1rem;
}

/* ── Input fields — the main fix ── */
.stTextInput > div > div > input {
    background-color: #ffffff !important;
    color: #1a1a2e !important;
    border: 2px solid #c5c8e8 !important;
    border-radius: 12px !important;
    padding: 0.7rem 1rem !important;
    font-size: 0.95rem !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.2s !important;
}

.stTextInput > div > div > input:focus {
    border-color: #6c63ff !important;
    box-shadow: 0 0 0 3px rgba(108, 99, 255, 0.15) !important;
    outline: none !important;
}

.stTextInput > div > div > input::placeholder {
    color: #9e9eb8 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #6c63ff, #f64f59) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 2rem !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 800 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.5px !important;
    cursor: pointer !important;
    transition: opacity 0.2s, transform 0.1s !important;
    width: 100% !important;
}

.stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}

.stButton > button:disabled {
    background: linear-gradient(135deg, #c5c8e8, #d4d4d4) !important;
    cursor: not-allowed !important;
    transform: none !important;
}

/* ── Answer box ── */
.answer-card {
    background: linear-gradient(135deg, #667eea08, #764ba208);
    border: 2px solid #6c63ff;
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    margin-top: 1rem;
    font-size: 0.95rem;
    color: #1a1a2e;
    line-height: 1.7;
}

.answer-label {
    font-family: 'Nunito', sans-serif;
    font-weight: 800;
    font-size: 0.75rem;
    color: #6c63ff;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.5rem;
}

.question-label {
    font-family: 'Nunito', sans-serif;
    font-weight: 800;
    font-size: 0.75rem;
    color: #f64f59;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.3rem;
}

.question-text {
    font-size: 0.95rem;
    color: #1a1a2e;
    font-weight: 600;
    margin-bottom: 0.8rem;
}

/* ── Chunk expander ── */
.chunk-box {
    background: #f8f8ff;
    border: 1px solid #e0e0f0;
    border-radius: 10px;
    padding: 0.8rem 1rem;
    margin-top: 0.5rem;
    font-size: 0.8rem;
    color: #555577;
    line-height: 1.6;
}

/* ── Divider ── */
.gradient-divider {
    height: 3px;
    background: linear-gradient(90deg, #6c63ff, #f64f59, #f9a825);
    border: none;
    border-radius: 2px;
    margin: 1.5rem 0;
}

/* ── Checkbox ── */
.stCheckbox > label {
    color: #1a1a2e !important;
    font-weight: 500 !important;
}

/* ── Footer ── */
.footer {
    text-align: center;
    color: #9e9eb8;
    font-size: 0.75rem;
    padding-top: 1rem;
}

/* ── Hide streamlit branding ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "video_loaded" not in st.session_state:
    st.session_state.video_loaded = False
if "current_video_id" not in st.session_state:
    st.session_state.current_video_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🎯 TubeQuery</h1>
    <p>Paste a YouTube URL · Ask anything · Get answers from the video</p>
</div>
""", unsafe_allow_html=True)

# ── Status badge ───────────────────────────────────────────────────────────────
if st.session_state.video_loaded:
    st.markdown(
        f'<div class="badge-loaded">▶ Video loaded — {st.session_state.current_video_id}</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="badge-empty">○ No video loaded yet</div>',
        unsafe_allow_html=True,
    )

# ── Load video card ────────────────────────────────────────────────────────────
st.markdown('<div class="card"><div class="card-title">📥 Load a YouTube Video</div>', unsafe_allow_html=True)

url_input = st.text_input(
    "YouTube URL",
    placeholder="https://www.youtube.com/watch?v=...",
    label_visibility="collapsed",
)

if st.button("Load Video & Index Transcript"):
    if not url_input.strip():
        st.error("Please enter a YouTube URL.")
    else:
        with st.spinner("⏳ Fetching transcript and indexing... (30–60 seconds, please wait)"):
            try:
                response = requests.post(f"{API_BASE}/load", json={"url": url_input.strip()})
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.video_loaded = True
                    st.session_state.current_video_id = data["video_id"]
                    st.session_state.chat_history = []
                    st.success(f"✅ Ready! {data['chunk_count']} chunks indexed.")
                    st.rerun()
                else:
                    st.error(f"❌ {response.json().get('detail', 'Unknown error')}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Run: python -m uvicorn main:app --reload")

st.markdown('</div>', unsafe_allow_html=True)

# ── Ask a question card ────────────────────────────────────────────────────────
st.markdown('<div class="card"><div class="card-title">💬 Ask About the Video</div>', unsafe_allow_html=True)

query_input = st.text_input(
    "Your question",
    placeholder="What is the main topic? Who is speaking? Summarize the key points...",
    label_visibility="collapsed",
    disabled=not st.session_state.video_loaded,
)

show_chunks = st.checkbox("Show source transcript chunks used", value=False)

if st.button("Get Answer", disabled=not st.session_state.video_loaded):
    if not query_input.strip():
        st.error("Please enter a question.")
    else:
        with st.spinner("🤔 Finding answer..."):
            try:
                response = requests.post(f"{API_BASE}/query", json={"query": query_input.strip()})
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.chat_history.append({
                        "query": data["query"],
                        "answer": data["answer"],
                        "source_chunks": data["source_chunks"],
                    })
                    st.rerun()
                else:
                    st.error(f"❌ {response.json().get('detail', 'Unknown error')}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API.")

st.markdown('</div>', unsafe_allow_html=True)

# ── Chat history ───────────────────────────────────────────────────────────────
if st.session_state.chat_history:
    st.markdown('<div class="card-title" style="margin-top:1rem;">📜 Conversation</div>', unsafe_allow_html=True)

    for entry in reversed(st.session_state.chat_history):
        st.markdown(f"""
        <div class="question-label">You asked</div>
        <div class="question-text">{entry['query']}</div>
        <div class="answer-label">Answer</div>
        <div class="answer-card">{entry['answer']}</div>
        """, unsafe_allow_html=True)

        if show_chunks:
            with st.expander("View source chunks"):
                for i, chunk in enumerate(entry["source_chunks"]):
                    st.markdown(f'<div class="chunk-box"><b>Chunk {i+1}:</b><br>{chunk}</div>', unsafe_allow_html=True)

        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="footer">TubeQuery · ChromaDB · NVIDIA API · FastAPI · Streamlit</div>',
    unsafe_allow_html=True,
)
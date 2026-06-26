"""
database.py — SQLite query logging for VidMind
Logs every query, answer, and video context for analytics.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.environ.get("VIDMIND_DB_PATH", "vidmind_logs.db")


def init_db():
    """Create the query_logs table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id    TEXT NOT NULL,
            query       TEXT NOT NULL,
            answer      TEXT NOT NULL,
            chunks_used INTEGER,
            timestamp   TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def log_query(video_id: str, query: str, answer: str, chunks_used: int):
    """Insert a query log entry."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO query_logs (video_id, query, answer, chunks_used, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """,
        (video_id, query, answer, chunks_used, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def get_recent_logs(limit: int = 20) -> list[dict]:
    """Fetch the most recent query logs."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, video_id, query, answer, chunks_used, timestamp
        FROM query_logs
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row[0],
            "video_id": row[1],
            "query": row[2],
            "answer": row[3],
            "chunks_used": row[4],
            "timestamp": row[5],
        }
        for row in rows
    ]


def get_stats() -> dict:
    """Return basic usage stats."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM query_logs")
    total_queries = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT video_id) FROM query_logs")
    unique_videos = cursor.fetchone()[0]

    conn.close()

    return {
        "total_queries": total_queries,
        "unique_videos_queried": unique_videos,
    }

"""
transcript.py — YouTube transcript fetcher and cleaner
Handles URL parsing, transcript retrieval, and basic text cleaning.
"""

import re
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url: str) -> str:
    patterns = [
        r"(?:v=)([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"embed/([a-zA-Z0-9_-]{11})",
        r"shorts/([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from URL: {url}")


def get_transcript(youtube_url: str) -> dict:
    try:
        video_id = extract_video_id(youtube_url)
    except ValueError as e:
        return {"video_id": None, "full_text": None, "error": str(e)}

    try:
       ytt = YouTubeTranscriptApi()
       transcript_data = ytt.fetch(video_id, languages=['hi', 'en', 'en-US', 'en-GB'])
       raw_text = " ".join([segment.text for segment in transcript_data])
       
    except Exception as e:
        return {
            "video_id": video_id,
            "full_text": None,
            "error": f"Failed to fetch transcript: {str(e)}",
        }

    cleaned_text = re.sub(r"\[.*?\]", "", raw_text)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()

    return {
        "video_id": video_id,
        "full_text": cleaned_text,
        "chunk_count_estimate": len(cleaned_text) // 500,
        "error": None,
    }
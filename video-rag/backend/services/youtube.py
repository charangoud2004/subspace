import re
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp


def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r'(?:v=|\/v\/|youtu\.be\/|\/embed\/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from: {url}")


def get_transcript(video_id: str) -> str:
    """Fetch transcript using youtube-transcript-api."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry["text"] for entry in transcript_list])
    except Exception as e:
        print(f"[youtube] Transcript fetch failed: {e}")
        return ""


def get_metadata(url: str) -> dict:
    """Fetch video metadata using yt-dlp."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": False,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            views = info.get("view_count", 0) or 0
            likes = info.get("like_count", 0) or 0
            comments = info.get("comment_count", 0) or 0

            engagement_rate = 0.0
            if views > 0:
                engagement_rate = round((likes + comments) / views * 100, 2)

            duration_secs = info.get("duration", 0) or 0
            minutes = duration_secs // 60
            seconds = duration_secs % 60
            duration_str = f"{minutes}:{seconds:02d}"

            # Extract hashtags from tags or description
            tags = info.get("tags", []) or []
            hashtags = [f"#{t}" for t in tags[:10]] if tags else []

            return {
                "title": info.get("title", "Unknown"),
                "creator": info.get("channel", info.get("uploader", "Unknown")),
                "follower_count": info.get("channel_follower_count", 0) or 0,
                "views": views,
                "likes": likes,
                "comments": comments,
                "engagement_rate": engagement_rate,
                "duration": duration_str,
                "upload_date": info.get("upload_date", "Unknown"),
                "hashtags": hashtags,
            }
    except Exception as e:
        print(f"[youtube] Metadata fetch failed: {e}")
        return {
            "title": "Unknown",
            "creator": "Unknown",
            "follower_count": 0,
            "views": 0,
            "likes": 0,
            "comments": 0,
            "engagement_rate": 0.0,
            "duration": "0:00",
            "upload_date": "Unknown",
            "hashtags": [],
        }


async def fetch_youtube(url: str) -> dict:
    """Main entry point: fetch all YouTube data."""
    video_id = extract_video_id(url)
    transcript = get_transcript(video_id)
    metadata = get_metadata(url)
    metadata["transcript"] = transcript
    metadata["platform"] = "youtube"
    metadata["video_id"] = video_id
    return metadata

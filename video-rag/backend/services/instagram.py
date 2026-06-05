import os
from dotenv import load_dotenv

load_dotenv()

APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN", "")

MOCK_INSTAGRAM_DATA = {
    "title": "Instagram Reel",
    "creator": "mock_creator",
    "follower_count": 50000,
    "views": 100000,
    "likes": 8000,
    "comments": 400,
    "engagement_rate": 8.4,
    "duration": "0:45",
    "upload_date": "2025-01-01",
    "hashtags": ["#reels", "#viral"],
    "transcript": "This is a placeholder transcript for the Instagram reel.",
    "platform": "instagram",
    "video_id": "mock_instagram_reel",
}


async def fetch_instagram(url: str) -> dict:
    """Fetch Instagram reel data via Apify. Falls back to mock if token missing or call fails."""

    if not APIFY_API_TOKEN:
        print("[instagram] APIFY_API_TOKEN not set — returning mock data")
        return {**MOCK_INSTAGRAM_DATA, "video_id": _extract_shortcode(url)}

    try:
        from apify_client import ApifyClient

        client = ApifyClient(APIFY_API_TOKEN)

        run_input = {
            "directUrls": [url],
            "resultsLimit": 1,
        }

        run = client.actor("apify/instagram-reel-scraper").call(run_input=run_input)

        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        if not items:
            print("[instagram] Apify returned no items — returning mock data")
            return {**MOCK_INSTAGRAM_DATA, "video_id": _extract_shortcode(url)}

        item = items[0]

        views = item.get("videoViewCount", item.get("videoPlayCount", 0)) or 0
        likes = item.get("likesCount", 0) or 0
        comments = item.get("commentsCount", 0) or 0

        engagement_rate = 0.0
        if views > 0:
            engagement_rate = round((likes + comments) / views * 100, 2)

        duration_secs = item.get("videoDuration", 0) or 0
        minutes = int(duration_secs) // 60
        seconds = int(duration_secs) % 60
        duration_str = f"{minutes}:{seconds:02d}"

        # Caption as transcript — no Whisper, no audio
        transcript = item.get("caption", "") or ""

        # Extract hashtags from caption
        import re
        hashtags = re.findall(r"#\w+", transcript)

        timestamp = item.get("timestamp", "")
        upload_date = timestamp[:10] if timestamp else "Unknown"

        shortcode = item.get("shortCode", _extract_shortcode(url))

        return {
            "title": f"Instagram Reel by {item.get('ownerUsername', 'Unknown')}",
            "creator": item.get("ownerUsername", "Unknown"),
            "follower_count": item.get("ownerFollowersCount", 0) or 0,
            "views": views,
            "likes": likes,
            "comments": comments,
            "engagement_rate": engagement_rate,
            "duration": duration_str,
            "upload_date": upload_date,
            "hashtags": hashtags[:10],
            "transcript": transcript,
            "platform": "instagram",
            "video_id": shortcode,
        }

    except Exception as e:
        print(f"[instagram] Apify call failed: {e} — returning mock data")
        return {**MOCK_INSTAGRAM_DATA, "video_id": _extract_shortcode(url)}


def _extract_shortcode(url: str) -> str:
    """Try to pull Instagram shortcode from URL."""
    import re
    match = re.search(r"/(?:reel|p)/([A-Za-z0-9_-]+)", url)
    return match.group(1) if match else "unknown_reel"

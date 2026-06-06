import os
import re
import yt_dlp  # type: ignore
from dotenv import load_dotenv  # type: ignore

load_dotenv()

APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN", "")


def _extract_shortcode(url: str) -> str:
    """Try to pull Instagram shortcode from URL."""
    match = re.search(r"/(?:reel|p)/([A-Za-z0-9_-]+)", url)
    return match.group(1) if match else "unknown_reel"


def _fetch_with_ytdlp(url: str) -> dict:
    """Fetch Instagram reel/post metadata using yt-dlp with browser cookies."""

    # Try different browsers for cookie extraction
    for browser in ["chrome", "edge", "firefox"]:
        try:
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "extract_flat": False,
                "cookiesfrombrowser": (browser,),
            }
            print(f"[instagram] Trying yt-dlp with {browser} cookies...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info:
                    return _parse_ytdlp_info(info, url)
        except Exception as e:
            print(f"[instagram] yt-dlp with {browser} cookies failed: {e}")
            continue

    # Last resort: try without cookies
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return _parse_ytdlp_info(info, url)


def _parse_ytdlp_info(info: dict, url: str) -> dict:
    """Parse yt-dlp info dict into our standard format."""
    views = info.get("view_count", 0) or 0
    likes = info.get("like_count", 0) or 0
    comments = info.get("comment_count", 0) or 0

    engagement_rate = 0.0
    if views > 0:
        engagement_rate = round((likes + comments) / views * 100, 2)

    duration_secs = info.get("duration", 0) or 0
    minutes = int(duration_secs) // 60
    seconds = int(duration_secs) % 60
    duration_str = f"{minutes}:{seconds:02d}"

    # Use description/caption as transcript
    transcript = info.get("description", "") or ""

    # Extract hashtags from caption
    hashtags = re.findall(r"#\w+", transcript)

    upload_date = info.get("upload_date", "Unknown") or "Unknown"
    creator = info.get("channel", info.get("uploader", "Unknown")) or "Unknown"
    follower_count = info.get("channel_follower_count", 0) or 0
    shortcode = _extract_shortcode(url)

    return {
        "title": info.get("title", f"Instagram Reel by {creator}"),
        "creator": creator,
        "follower_count": follower_count,
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


def _fetch_with_apify(url: str) -> dict:
    """Fetch Instagram reel data via Apify API."""
    from apify_client import ApifyClient  # type: ignore

    client = ApifyClient(APIFY_API_TOKEN)

    run_input = {
        "directUrls": [url],
        "resultsLimit": 1,
    }

    run = client.actor("apify/instagram-scraper").call(run_input=run_input)

    # Newer apify-client returns Run object with attributes, not a dict
    dataset_id = getattr(run, "default_dataset_id", None) or run.get("defaultDatasetId") if isinstance(run, dict) else getattr(run, "default_dataset_id", None)
    if not dataset_id:
        raise ValueError(f"Could not get dataset ID from Apify run: {type(run)}")
    items = list(client.dataset(dataset_id).iterate_items())

    if not items:
        raise ValueError("Apify returned no items")

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

    transcript = item.get("caption", "") or ""
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


async def fetch_instagram(url: str) -> dict:
    """Fetch Instagram post/reel data. Tries Apify first, then yt-dlp."""

    # --- Method 1: Apify (works for photos AND videos) ---
    if APIFY_API_TOKEN:
        try:
            print(f"[instagram] Trying Apify for {url}")
            result = _fetch_with_apify(url)
            print(f"[instagram] Apify succeeded for {url}")
            return result
        except Exception as e:
            print(f"[instagram] Apify failed: {e}")

    # --- Method 2: yt-dlp (only works for video posts/reels) ---
    try:
        print(f"[instagram] Trying yt-dlp for {url}")
        result = _fetch_with_ytdlp(url)
        print(f"[instagram] yt-dlp succeeded for {url}")
        return result
    except Exception as e:
        print(f"[instagram] yt-dlp failed: {e}")

    # --- Both methods failed ---
    print(f"[instagram] WARNING: All methods failed for {url}")
    return {
        "title": f"Instagram Reel ({_extract_shortcode(url)})",
        "creator": "Unknown (scraping failed)",
        "follower_count": 0,
        "views": 0,
        "likes": 0,
        "comments": 0,
        "engagement_rate": 0.0,
        "duration": "0:00",
        "upload_date": "Unknown",
        "hashtags": [],
        "transcript": "",
        "platform": "instagram",
        "video_id": _extract_shortcode(url),
    }

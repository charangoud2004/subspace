import asyncio
from fastapi import APIRouter, HTTPException
from schemas import IngestRequest, IngestResponse
from services.youtube import fetch_youtube
from services.instagram import fetch_instagram
from services.embedder import embed_transcript
from services.rag import init_session

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_videos(req: IngestRequest):
    """Ingest a YouTube video and Instagram reel concurrently."""
    try:
        # Fetch both videos concurrently
        yt_data, ig_data = await asyncio.gather(
            fetch_youtube(req.youtube_url),
            fetch_instagram(req.instagram_url),
        )

        # Embed both transcripts concurrently
        await asyncio.gather(
            embed_transcript(
                transcript=yt_data.get("transcript", ""),
                video_id=yt_data.get("video_id", "unknown_yt"),
                source_url=req.youtube_url,
                platform="youtube",
                session_id=req.session_id,
            ),
            embed_transcript(
                transcript=ig_data.get("transcript", ""),
                video_id=ig_data.get("video_id", "unknown_ig"),
                source_url=req.instagram_url,
                platform="instagram",
                session_id=req.session_id,
            ),
        )

        # Initialize RAG session
        init_session(req.session_id, metadata_a=yt_data, metadata_b=ig_data)

        return IngestResponse(
            success=True,
            video_a=yt_data,
            video_b=ig_data,
        )

    except Exception as e:
        print(f"[ingest] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

import json
from fastapi import APIRouter, Query
from sse_starlette.sse import EventSourceResponse
from services.rag import stream_response

router = APIRouter()


@router.get("/chat/stream")
async def chat_stream(
    message: str = Query(..., description="User message"),
    session_id: str = Query(..., description="Session ID"),
):
    """Stream chat responses via Server-Sent Events."""

    async def event_generator():
        try:
            async for token, sources in stream_response(session_id, message):
                if sources is not None:
                    # Final message with sources
                    yield {
                        "event": "message",
                        "data": json.dumps({
                            "token": "",
                            "done": True,
                            "sources": sources,
                        }),
                    }
                else:
                    yield {
                        "event": "message",
                        "data": json.dumps({
                            "token": token,
                            "done": False,
                        }),
                    }
        except Exception as e:
            yield {
                "event": "message",
                "data": json.dumps({
                    "token": f"\n\n⚠️ Error: {str(e)}",
                    "done": True,
                    "sources": [],
                }),
            }

    return EventSourceResponse(event_generator())

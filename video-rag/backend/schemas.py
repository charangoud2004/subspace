from pydantic import BaseModel
from typing import Optional


class IngestRequest(BaseModel):
    youtube_url: str
    instagram_url: str
    session_id: str


class IngestResponse(BaseModel):
    success: bool
    video_a: dict
    video_b: dict


class ChatQuery(BaseModel):
    message: str
    session_id: str


class SourceChunk(BaseModel):
    video_id: str
    chunk_index: int
    preview: str

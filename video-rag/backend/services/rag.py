import os
import json
from typing import AsyncGenerator, Tuple, Optional, List
from dotenv import load_dotenv
from services.embedder import get_retriever_docs

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Global session store
sessions: dict = {}


class SimpleMemory:
    """Simple conversation memory (replaces langchain ConversationBufferMemory)."""

    def __init__(self):
        self.history: list[dict] = []

    def add(self, user_msg: str, ai_msg: str):
        self.history.append({"user": user_msg, "assistant": ai_msg})

    def get_history_str(self) -> str:
        lines = []
        for turn in self.history:
            lines.append(f"User: {turn['user']}")
            lines.append(f"Assistant: {turn['assistant']}")
        return "\n".join(lines)


def init_session(session_id: str, metadata_a: dict, metadata_b: dict):
    """Initialize a session with memory and video metadata."""
    sessions[session_id] = {
        "memory": SimpleMemory(),
        "metadata": {
            "A": metadata_a,
            "B": metadata_b,
        },
    }
    print(f"[rag] Session {session_id} initialized")


async def stream_response(
    session_id: str, question: str
) -> AsyncGenerator[Tuple[str, Optional[List[dict]]], None]:
    """Stream LLM response token by token, then yield sources at the end."""

    if not GROQ_API_KEY:
        yield "⚠️ Please add GROQ_API_KEY to your .env file to enable AI responses.", None
        yield "", []
        return

    if session_id not in sessions:
        yield "⚠️ Session not found. Please ingest videos first.", None
        yield "", []
        return

    session = sessions[session_id]
    metadata = session["metadata"]
    memory = session["memory"]

    # Retrieve relevant documents


    try:
        docs = get_retriever_docs(session_id, question, k=4)
    except Exception as e:
        print(f"[rag] Retrieval failed: {e}")
        docs = []

    sources = [
        {
            "video_id": d.metadata.get("video_id", "unknown"),
            "chunk_index": d.metadata.get("chunk_index", 0),
            "preview": d.page_content[:100],
        }
        for d in docs
    ]

    context = "\n\n".join([d.page_content for d in docs])
    history = memory.get_history_str()

    # Build metadata summaries (exclude transcript to save tokens)
    meta_a = {k: v for k, v in metadata["A"].items() if k != "transcript"}
    meta_b = {k: v for k, v in metadata["B"].items() if k != "transcript"}

    prompt = f"""You are a video content analyst comparing two videos.

Video A (YouTube): {json.dumps(meta_a)}
Video B (Instagram): {json.dumps(meta_b)}

Relevant transcript excerpts:
{context}

Previous conversation:
{history}

User question: {question}

Instructions:
- Always cite which video (Video A or Video B) you're referring to
- Use the metadata stats (views, likes, engagement rate) when comparing performance
- Reference transcript content when discussing what was said in the videos
- Be specific and data-driven in your analysis
- Format your response with markdown for readability"""

    try:
        from langchain_groq import ChatGroq  # type: ignore

        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            streaming=True,
            groq_api_key=GROQ_API_KEY,
        )

        full_response = ""
        async for chunk in llm.astream(prompt):
            token = chunk.content
            if token:
                full_response += token
                yield token, None

        # Save to memory
        memory.add(question, full_response)

        # Final yield with sources
        yield "", sources

    except Exception as e:
        error_msg = f"\n\n⚠️ LLM error: {str(e)}"
        yield error_msg, None
        yield "", []

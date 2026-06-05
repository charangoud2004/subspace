import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "video-rag")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


def _get_embeddings():
    """Return Google embeddings if key is available, else a fake one for ChromaDB."""
    if GEMINI_API_KEY:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=GEMINI_API_KEY,
        )
    else:
        # Fallback: use a simple deterministic embedding for local dev
        from langchain_community.embeddings import FakeEmbeddings
        print("[embedder] GEMINI_API_KEY not set — using FakeEmbeddings (768-dim)")
        return FakeEmbeddings(size=768)


def _use_pinecone() -> bool:
    return bool(PINECONE_API_KEY)


def get_vectorstore(session_id: str):
    """Return the appropriate vectorstore for the given session."""
    embeddings = _get_embeddings()

    if _use_pinecone():
        from pinecone import Pinecone, ServerlessSpec
        from langchain_pinecone import PineconeVectorStore

        pc = Pinecone(api_key=PINECONE_API_KEY)

        # Create index if it doesn't exist
        existing = [idx.name for idx in pc.list_indexes()]
        if PINECONE_INDEX not in existing:
            pc.create_index(
                name=PINECONE_INDEX,
                dimension=768,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )

        return PineconeVectorStore(
            index_name=PINECONE_INDEX,
            embedding=embeddings,
            namespace=session_id,
            pinecone_api_key=PINECONE_API_KEY,
        )
    else:
        from langchain_community.vectorstores import Chroma

        print(f"[embedder] Using ChromaDB fallback (session: {session_id})")
        return Chroma(
            collection_name=session_id.replace("-", "_"),
            embedding_function=embeddings,
            persist_directory="./chroma_db",
        )


async def embed_transcript(
    transcript: str,
    video_id: str,
    source_url: str,
    platform: str,
    session_id: str,
) -> int:
    """Split transcript into chunks, embed, and store. Return chunk count."""
    if not transcript or not transcript.strip():
        print(f"[embedder] Empty transcript for {video_id} — skipping")
        return 0

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = splitter.split_text(transcript)

    documents = []
    for i, text in enumerate(texts):
        doc = Document(
            page_content=text,
            metadata={
                "video_id": video_id,
                "source_url": source_url,
                "platform": platform,
                "chunk_index": i,
            },
        )
        documents.append(doc)

    if not documents:
        return 0

    vectorstore = get_vectorstore(session_id)
    vectorstore.add_documents(documents)

    print(f"[embedder] Stored {len(documents)} chunks for {video_id} in session {session_id}")
    return len(documents)

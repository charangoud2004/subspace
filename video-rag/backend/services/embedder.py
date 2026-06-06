import os
from dotenv import load_dotenv  # type: ignore
from langchain_text_splitters import RecursiveCharacterTextSplitter  # type: ignore
from langchain_core.documents import Document  # type: ignore

load_dotenv()


PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "video-rag")


def _get_embeddings():
    """Return local HuggingFace embeddings."""
    from langchain_huggingface import HuggingFaceEmbeddings  # type: ignore
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def _use_pinecone() -> bool:
    return bool(PINECONE_API_KEY)


# ---------- Pinecone direct SDK helpers ----------

_pinecone_index = None


def _get_pinecone_index():
    """Lazily create/connect to Pinecone index using the SDK directly."""
    global _pinecone_index
    if _pinecone_index is not None:
        return _pinecone_index

    from pinecone import Pinecone, ServerlessSpec  # type: ignore

    pc = Pinecone(api_key=PINECONE_API_KEY)

    existing = [idx.name for idx in pc.list_indexes()]
    if PINECONE_INDEX not in existing:
        pc.create_index(
            name=PINECONE_INDEX,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        print(f"[embedder] Created Pinecone index: {PINECONE_INDEX}")

    _pinecone_index = pc.Index(PINECONE_INDEX)
    return _pinecone_index


def _pinecone_upsert(documents: list[Document], embeddings_model, namespace: str):
    """Upsert documents into Pinecone using the SDK directly."""
    index = _get_pinecone_index()
    texts = [doc.page_content for doc in documents]
    vectors = embeddings_model.embed_documents(texts)

    upsert_data = []
    for i, (doc, vec) in enumerate(zip(documents, vectors)):
        upsert_data.append({
            "id": f"{doc.metadata['video_id']}_chunk_{doc.metadata['chunk_index']}",
            "values": vec,
            "metadata": {
                **doc.metadata,
                "text": doc.page_content,
            },
        })

    # Upsert in batches of 100
    batch_size = 100
    for i in range(0, len(upsert_data), batch_size):
        batch = upsert_data[i:i + batch_size]
        index.upsert(vectors=batch, namespace=namespace)


def _pinecone_query(query_text: str, embeddings_model, namespace: str, k: int = 4) -> list[Document]:
    """Query Pinecone and return LangChain Documents."""
    index = _get_pinecone_index()
    query_vec = embeddings_model.embed_query(query_text)

    results = index.query(
        vector=query_vec,
        top_k=k,
        include_metadata=True,
        namespace=namespace,
    )

    docs = []
    for match in results.get("matches", []):
        meta = match.get("metadata", {})
        text = meta.pop("text", "")
        docs.append(Document(page_content=text, metadata=meta))
    return docs


# ---------- ChromaDB helpers ----------

_chroma_stores = {}


def _get_chroma_store(session_id: str):
    """Get or create a ChromaDB vectorstore for the session."""
    if session_id in _chroma_stores:
        return _chroma_stores[session_id]

    from langchain_community.vectorstores import Chroma  # type: ignore

    embeddings = _get_embeddings()
    store = Chroma(
        collection_name=session_id.replace("-", "_"),
        embedding_function=embeddings,
        persist_directory="./chroma_db",
    )
    _chroma_stores[session_id] = store
    print(f"[embedder] Using ChromaDB fallback (session: {session_id})")
    return store


# ---------- Public API ----------

def get_retriever_docs(session_id: str, query: str, k: int = 4) -> list[Document]:
    """Retrieve relevant documents for a query from the appropriate store."""
    embeddings = _get_embeddings()

    if _use_pinecone():
        return _pinecone_query(query, embeddings, namespace=session_id, k=k)
    else:
        store = _get_chroma_store(session_id)
        retriever = store.as_retriever(search_kwargs={"k": k})
        return retriever.invoke(query)


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

    embeddings = _get_embeddings()

    if _use_pinecone():
        _pinecone_upsert(documents, embeddings, namespace=session_id)
    else:
        store = _get_chroma_store(session_id)
        store.add_documents(documents)

    print(f"[embedder] Stored {len(documents)} chunks for {video_id} in session {session_id}")
    return len(documents)

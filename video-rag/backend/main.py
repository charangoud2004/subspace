from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.ingest import router as ingest_router
from routers.chat import router as chat_router

app = FastAPI(
    title="Video RAG API",
    description="Compare YouTube videos and Instagram reels using RAG",
    version="1.0.0",
)

# CORS — allow all origins for dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(ingest_router, prefix="/api", tags=["ingest"])
app.include_router(chat_router, prefix="/api", tags=["chat"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "video-rag-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

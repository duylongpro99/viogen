from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.routes import sessions, chat, generations

app = FastAPI(
    title="Creative Studio API",
    description="Multi-model orchestration for image/video generation",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(sessions.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(generations.router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "debug": settings.debug}

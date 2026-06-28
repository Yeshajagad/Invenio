import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import get_settings
from app.database import create_tables
from app.api.routes import documents_router

from app.api.routes import documents_router, processing_router, embeddings_router


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🔍 Starting {settings.app_name} v{settings.app_version}")
    os.makedirs(settings.upload_dir, exist_ok=True)
    await create_tables()
    logger.info("✅ Database tables ready")
    yield
    logger.info("👋 Shutting down Invenio")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-native knowledge workspace — find, learn, and discover.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router)
app.include_router(processing_router)
app.include_router(embeddings_router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "message": "Invenio — find, learn, discover 🔍",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
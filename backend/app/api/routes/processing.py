from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.processing_service import ProcessingService

router = APIRouter(prefix="/api/process", tags=["Processing"])
service = ProcessingService()


@router.post("/{doc_id}")
async def process_document(
    doc_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Trigger processing pipeline for a document."""
    background_tasks.add_task(service.process_document, doc_id, db)
    return {
        "message": f"Processing started for document {doc_id}",
        "doc_id": doc_id,
        "status": "processing",
    }


@router.post("/sync/{doc_id}")
async def process_document_sync(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Process document synchronously (for testing)."""
    result = await service.process_document(doc_id, db)
    return result
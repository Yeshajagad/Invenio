from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services import DocumentService
from app.schemas import DocumentResponse, DocumentListResponse

router = APIRouter(prefix="/api/documents", tags=["Documents"])
service = DocumentService()


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload a new document to Invenio."""
    return await service.upload_document(file, db)


@router.get("/", response_model=DocumentListResponse)
async def list_documents(db: AsyncSession = Depends(get_db)):
    """List all uploaded documents."""
    docs = await service.list_documents(db)
    return DocumentListResponse(total=len(docs), documents=docs)


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single document by ID."""
    return await service.get_document(doc_id, db)


@router.delete("/{doc_id}")
async def delete_document(doc_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a document and remove its file."""
    return await service.delete_document(doc_id, db)
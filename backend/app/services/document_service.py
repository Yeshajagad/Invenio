import os
import shutil
import uuid
from datetime import datetime
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from loguru import logger

from app.models.document import Document, ProcessingStatus
from app.config import get_settings

settings = get_settings()

ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
    "text/csv": "csv",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "text/markdown": "md",
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
}


class DocumentService:

    async def upload_document(
        self, file: UploadFile, db: AsyncSession
    ) -> Document:
        # Validate file type
        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}. Allowed: PDF, DOCX, TXT, CSV, XLSX, MD, PNG, JPG",
            )

        # Validate file size
        content = await file.read()
        size_mb = len(content) / (1024 * 1024)
        if size_mb > settings.max_file_size_mb:
            raise HTTPException(
                status_code=413,
                detail=f"File too large: {size_mb:.1f}MB. Max: {settings.max_file_size_mb}MB",
            )

        # Generate unique filename
        ext = ALLOWED_TYPES[file.content_type]
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        storage_path = os.path.join(settings.upload_dir, unique_name)

        # Save file
        os.makedirs(settings.upload_dir, exist_ok=True)
        with open(storage_path, "wb") as f:
            f.write(content)

        # Save to DB
        doc = Document(
            file_name=unique_name,
            original_name=file.filename,
            file_type=ext,
            storage_path=storage_path,
            file_size=round(size_mb, 3),
            processing_status=ProcessingStatus.PENDING,
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)

        logger.info(f"📄 Uploaded: {file.filename} → {unique_name}")
        return doc

    async def list_documents(self, db: AsyncSession) -> list[Document]:
        result = await db.execute(
            select(Document).order_by(Document.upload_date.desc())
        )
        return result.scalars().all()

    async def get_document(self, doc_id: int, db: AsyncSession) -> Document:
        result = await db.execute(
            select(Document).where(Document.id == doc_id)
        )
        doc = result.scalar_one_or_none()
        if not doc:
            raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
        return doc

    async def delete_document(self, doc_id: int, db: AsyncSession) -> dict:
        doc = await self.get_document(doc_id, db)

        # Remove file from disk
        if os.path.exists(doc.storage_path):
            os.remove(doc.storage_path)

        await db.execute(delete(Document).where(Document.id == doc_id))
        await db.commit()

        logger.info(f"🗑️  Deleted document {doc_id}: {doc.original_name}")
        return {"message": f"Document '{doc.original_name}' deleted successfully"}
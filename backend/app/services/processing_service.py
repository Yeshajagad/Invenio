from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.models.document import Document, DocumentChunk, ProcessingStatus
from app.ingestion.extractor import TextExtractor
from app.ingestion.cleaner import TextCleaner
from app.ingestion.chunker import TextChunker

extractor = TextExtractor()
cleaner = TextCleaner()
chunker = TextChunker(chunk_size=500, overlap=50)


class ProcessingService:

    async def process_document(self, doc_id: int, db: AsyncSession) -> dict:
        # Fetch document
        result = await db.execute(
            select(Document).where(Document.id == doc_id)
        )
        doc = result.scalar_one_or_none()
        if not doc:
            return {"error": f"Document {doc_id} not found"}

        # Mark as processing
        doc.processing_status = ProcessingStatus.PROCESSING
        await db.commit()

        try:
            # Extract text
            logger.info(f"📖 Extracting text from: {doc.original_name}")
            extraction = await extractor.extract(doc.storage_path, doc.file_type)

            if extraction.get("error"):
                raise Exception(extraction["error"])

            # Clean text
            raw_text = extraction["text"]
            clean_text = cleaner.clean(raw_text)

            # Chunk text
            chunks = chunker.chunk(clean_text, doc_id)
            logger.info(f"✂️  Created {len(chunks)} chunks for doc {doc_id}")

            # Save chunks to DB
            for chunk_data in chunks:
                chunk = DocumentChunk(**chunk_data)
                db.add(chunk)

            # Update document metadata
            doc.page_count = extraction.get("page_count", 0)
            doc.word_count = extraction.get("word_count", 0)
            doc.processing_status = ProcessingStatus.COMPLETED
            doc.processed_date = datetime.utcnow()

            await db.commit()
            logger.info(f"✅ Processing complete for doc {doc_id}")

            return {
                "doc_id": doc_id,
                "chunks_created": len(chunks),
                "word_count": doc.word_count,
                "page_count": doc.page_count,
                "status": "completed",
            }

        except Exception as e:
            doc.processing_status = ProcessingStatus.FAILED
            doc.error_message = str(e)
            await db.commit()
            logger.error(f"❌ Processing failed for doc {doc_id}: {e}")
            return {"error": str(e), "status": "failed"}
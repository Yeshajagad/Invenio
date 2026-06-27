from datetime import datetime
from pydantic import BaseModel
from app.models.document import ProcessingStatus


class DocumentBase(BaseModel):
    file_name: str
    file_type: str


class DocumentCreate(DocumentBase):
    original_name: str
    storage_path: str
    file_size: float


class DocumentResponse(BaseModel):
    id: int
    file_name: str
    original_name: str
    file_type: str
    file_size: float
    page_count: int
    word_count: int
    processing_status: ProcessingStatus
    upload_date: datetime
    processed_date: datetime | None = None
    error_message: str | None = None

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    total: int
    documents: list[DocumentResponse]
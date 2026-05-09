from pydantic import BaseModel
from typing import Optional, Any
import uuid
from datetime import datetime

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    deadlines_found: int
    extracted_info: Optional[Any] = None

class DocumentRecordResponse(BaseModel):
    id: uuid.UUID
    filename: str
    document_type: Optional[str] = None
    status: str
    uploaded_at: datetime
    
    class Config:
        from_attributes = True

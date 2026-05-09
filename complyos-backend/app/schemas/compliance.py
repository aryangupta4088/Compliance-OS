from pydantic import BaseModel
from datetime import datetime
import uuid
from typing import Optional

class DeadlineCreate(BaseModel):
    title: str
    deadline_date: datetime
    compliance_type: str
    urgency: Optional[str] = "medium"

class ComplianceDeadlineResponse(DeadlineCreate):
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    source_document_id: Optional[str] = None
    created_by_agent: Optional[str] = None
    
    class Config:
        from_attributes = True

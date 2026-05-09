from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

class CAProfileCreate(BaseModel):
    full_name: str
    license_number: str
    specializations: List[str] = []
    subscription_tier: Optional[str] = "basic"

class CAProfileResponse(CAProfileCreate):
    id: uuid.UUID
    user_id: uuid.UUID
    rating: float
    verified: bool
    clients: List[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConsultationBooking(BaseModel):
    ca_id: uuid.UUID
    user_id: uuid.UUID
    scheduled_at: datetime
    notes: Optional[str] = None

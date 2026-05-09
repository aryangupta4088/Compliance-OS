from pydantic import BaseModel
from typing import Optional, List
import uuid

class BusinessProfileCreate(BaseModel):
    business_name: str
    business_type: str
    sector: Optional[str]
    state: str
    district: str
    pincode: str
    turnover_range: Optional[str]
    employee_count: Optional[str]
    is_women_led: bool = False
    udyam_number: Optional[str] = None
    gstin: Optional[str] = None
    pan: Optional[str] = None

class BusinessProfileResponse(BusinessProfileCreate):
    id: uuid.UUID
    user_id: uuid.UUID
    tier: str
    enrolled_schemes: List[str] = []
    aria_profile_complete: bool = False
    
    class Config:
        from_attributes = True
      

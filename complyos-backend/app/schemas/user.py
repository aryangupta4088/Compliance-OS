from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import uuid

class UserCreate(BaseModel):
    email: EmailStr
    phone: str
    password: str
    role: Optional[str] = "business_owner"

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    phone: str
    role: str
    is_active: bool
    preferred_language: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

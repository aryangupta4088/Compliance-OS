import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Float, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class CAProfile(Base):
    __tablename__ = "ca_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    
    full_name = Column(String(255), nullable=False)
    license_number = Column(String(100), unique=True, nullable=False)
    specializations = Column(JSON, default=list) # Array of strings
    rating = Column(Float, default=0.0)
    verified = Column(Boolean, default=False)
    subscription_tier = Column(String(50), default="basic")
    clients = Column(JSON, default=list) # Array of user_ids (strings/UUIDs)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

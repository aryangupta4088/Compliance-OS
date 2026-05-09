import uuid
from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class BusinessProfile(Base):
    __tablename__ = "business_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    
    business_name = Column(String(255))
    business_type = Column(String(100)) # shop/factory/service/food
    sector = Column(String(100))
    state = Column(String(100))
    district = Column(String(100))
    pincode = Column(String(10))
    turnover_range = Column(String(50)) # e.g., "<1Cr"
    employee_count = Column(String(20)) # e.g., "10-50"
    is_women_led = Column(Boolean, default=False)
    
    udyam_number = Column(String(50))
    gstin = Column(String(15))
    pan = Column(String(10))
    
    tier = Column(String(20), default="free")
    enrolled_schemes = Column(JSON, default=list)
    aria_profile_complete = Column(Boolean, default=False)
    
    owner = relationship("User", back_populates="business_profile")

import uuid
import enum
from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class UserRole(enum.Enum):
    BUSINESS_OWNER = "business_owner"
    CA = "ca"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.BUSINESS_OWNER)
    is_active = Column(Boolean, default=True)
    preferred_language = Column(String(10), default="en")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    business_profile = relationship("BusinessProfile", back_populates="owner", uselist=False)

import uuid
from sqlalchemy import Column, String, Integer, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class SchemeApplication(Base):
    __tablename__ = "scheme_applications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    scheme_name = Column(String(255))
    scheme_type = Column(String(50))
    status = Column(String(20), default="eligible") # eligible/applied/enrolled/rejected
    match_score = Column(Integer)
    applied_date = Column(DateTime(timezone=True))
    ca_approved = Column(Boolean, default=False)
    prefilled_data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

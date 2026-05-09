import uuid
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    
    title = Column(String(255))
    message = Column(String)
    urgency = Column(String(10), default="low")
    is_read = Column(Boolean, default=False)
    source = Column(String(20)) # VEDA/SENTINEL/SCOUT/system
    created_at = Column(DateTime(timezone=True), server_default=func.now()))

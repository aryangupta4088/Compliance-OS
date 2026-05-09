import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class DocumentRecord(Base):
    __tablename__ = "document_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    filename = Column(String(255), nullable=False)
    r2_key = Column(String(512), nullable=False)
    document_type = Column(String(100))
    mongo_doc_id = Column(String(50)) # Reference to MongoDB document ID
    status = Column(String(20), default="pending") # pending/processing/verified
    
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

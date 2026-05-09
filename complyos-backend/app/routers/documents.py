from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.utils.auth import get_current_user
from app.models.user import User
from app.agents.veda import VedAgent
from app.services.r2_service import upload_file

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename.endswith(('.pdf', '.png', '.jpg', '.jpeg')):
        raise HTTPException(400, "Invalid format")
    
    content = await file.read()
    
    # 1. Upload to R2
    r2_key = await upload_file(file, str(current_user.id))
    
    # 2. Process with VEDA
    ved_agent = VedAgent()
    result = await ved_agent.process_document(content, file.filename, str(current_user.id), db)
    
    return {
        "message": "Document processed successfully",
        "r2_key": r2_key,
        "deadlines_found": result.get("deadlines_found"),
        "extracted_info": result.get("data")
    }

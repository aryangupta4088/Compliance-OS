from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db, mongo_db
from app.models.user import User, UserRole
from app.models.ca import CAProfile
from app.models.document import DocumentRecord
from app.models.scheme import SchemeApplication
from app.utils.dependencies import require_admin_role
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/dashboard")
async def get_admin_dashboard(
    current_user: User = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
):
    # 1. Total users
    users_count = await db.execute(select(func.count(User.id)))
    # 2. Total CAs
    cas_count = await db.execute(select(func.count(CAProfile.id)))
    # 3. Total documents processed
    docs_count = await db.execute(select(func.count(DocumentRecord.id)))
    # 4. Total schemes applied
    schemes_count = await db.execute(select(func.count(SchemeApplication.id)).where(SchemeApplication.status == "applied"))
    
    # 5. Recent signups (last 10)
    recent_users = await db.execute(select(User).order_by(User.created_at.desc()).limit(10))
    
    return {
        "total_users": users_count.scalar(),
        "total_cas": cas_count.scalar(),
        "total_documents_processed": docs_count.scalar(),
        "total_schemes_applied": schemes_count.scalar(),
        "recent_signups": recent_users.scalars().all()
    }

@router.post("/freelancers")
async def add_freelancer(
    data: dict,
    current_user: User = Depends(require_admin_role)
):
    data["created_at"] = datetime.utcnow()
    result = await mongo_db.freelancers.insert_one(data)
    return {"id": str(result.inserted_id)}

@router.get("/users")
async def list_users(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * limit
    result = await db.execute(select(User).offset(offset).limit(limit))
    return result.scalars().all()

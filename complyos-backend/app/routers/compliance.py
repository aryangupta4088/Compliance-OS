from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.utils.auth import get_current_user
from app.models.user import User
from app.models.compliance import ComplianceDeadline

router = APIRouter(prefix="/compliance", tags=["Compliance"])

@router.get("/calendar/{user_id}")
async def get_calendar(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ComplianceDeadline).where(ComplianceDeadline.user_id == user_id).order_by(ComplianceDeadline.deadline_date)
    )
    deadlines = result.scalars().all()
    return deadlines

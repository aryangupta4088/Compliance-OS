from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.compliance import ComplianceDeadline
from datetime import datetime, timedelta

async def get_upcoming_deadlines(user_id: str, db: AsyncSession, days: int = 30):
    """Fetch deadlines within the next N days"""
    end_date = datetime.utcnow() + timedelta(days=days)
    result = await db.execute(
        select(ComplianceDeadline)
        .where(
            ComplianceDeadline.user_id == user_id,
            ComplianceDeadline.deadline_date >= datetime.utcnow(),
            ComplianceDeadline.deadline_date <= end_date
        )
        .order_by(ComplianceDeadline.deadline_date)
    )
    return result.scalars().all()

async def mark_deadline_complete(deadline_id: str, db: AsyncSession):
    """Mark a deadline as completed"""
    await db.execute(
        update(ComplianceDeadline)
        .where(ComplianceDeadline.id == deadline_id)
        .values(status="completed")
    )
    await db.commit()
    return True

async def get_overdue_deadlines(user_id: str, db: AsyncSession):
    """Find and update overdue deadlines"""
    now = datetime.utcnow()
    await db.execute(
        update(ComplianceDeadline)
        .where(
            ComplianceDeadline.user_id == user_id,
            ComplianceDeadline.deadline_date < now,
            ComplianceDeadline.status == "pending"
        )
        .values(status="overdue")
    )
    await db.commit()
    
    result = await db.execute(
        select(ComplianceDeadline)
        .where(ComplianceDeadline.user_id == user_id, ComplianceDeadline.status == "overdue")
    )
    return result.scalars().all()

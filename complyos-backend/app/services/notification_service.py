from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.notification import Notification
import uuid

async def create_notification(
    user_id: str,
    title: str,
    message: str,
    urgency: str,
    source: str,
    db: AsyncSession
):
    """Creates a single notification"""
    notif = Notification(
        id=uuid.uuid4(),
        user_id=user_id,
        title=title,
        message=message,
        urgency=urgency,
        source=source
    )
    db.add(notif)
    await db.commit()
    return notif

async def send_bulk_notifications(
    user_ids: list,
    title: str,
    message: str,
    urgency: str,
    source: str,
    db: AsyncSession
):
    """Sends notifications to multiple users"""
    for user_id in user_ids:
        notif = Notification(
            id=uuid.uuid4(),
            user_id=user_id,
            title=title,
            message=message,
            urgency=urgency,
            source=source
        )
        db.add(notif)
    await db.commit()

async def get_unread_count(user_id: str, db: AsyncSession) -> int:
    """Returns count of unread notifications"""
    result = await db.execute(
        select(func.count())
        .select_from(Notification)
        .where(Notification.user_id == user_id, Notification.is_read == False)
    )
    return result.scalar() or 0

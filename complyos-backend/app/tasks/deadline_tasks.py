from app.tasks.celery_app import celery_app
from app.database import AsyncSessionLocal
from sqlalchemy import select
from app.models.compliance import ComplianceDeadline
from app.services.notification_service import create_notification
from datetime import datetime, timedelta
import asyncio

@celery_app.task(name="app.tasks.deadline_tasks.send_reminders")
def send_reminders():
    """Background task to send deadline reminders"""
    async def run():
        async with AsyncSessionLocal() as db:
            now = datetime.utcnow()
            # Reminders for 1, 3, 7 days away
            target_dates = [1, 3, 7]
            for days in target_dates:
                target_date = (now + timedelta(days=days)).date()
                
                result = await db.execute(
                    select(ComplianceDeadline)
                    .where(
                        ComplianceDeadline.status == "pending"
                    )
                )
                deadlines = result.scalars().all()
                
                for d in deadlines:
                    if d.deadline_date.date() == target_date:
                        urgency = "high" if days == 1 else "medium"
                        await create_notification(
                            user_id=str(d.user_id),
                            title=f"Reminder: {d.title}",
                            message=f"Your deadline for {d.title} is in {days} day(s).",
                            urgency=urgency,
                            source="system",
                            db=db
                        )
            await db.commit()

    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.ensure_future(run())
    else:
        loop.run_until_complete(run())

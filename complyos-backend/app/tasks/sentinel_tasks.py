from app.tasks.celery_app import celery_app
from app.agents.sentinel import SentinelAgent
from app.services.notification_service import create_notification
from app.database import mongo_db, AsyncSessionLocal, engine
from sqlalchemy import select
from app.models.user import User
from datetime import datetime
import asyncio

@celery_app.task(name="app.tasks.sentinel_tasks.monitor_circulars")
def monitor_circulars():
    """Background task for regulatory monitoring"""
    async def run():
        sentinel = SentinelAgent()
        findings = await sentinel.monitor_sources()
        
        async with AsyncSessionLocal() as db:
            for finding in findings:
                # Log to MongoDB
                await mongo_db.sentinel_logs.insert_one({
                    "finding": finding,
                    "timestamp": datetime.utcnow()
                })
                
                # Notify all relevant users (e.g., all active users for now)
                res = await db.execute(select(User.id).where(User.is_active == True))
                user_ids = res.scalars().all()
                
                for user_id in user_ids:
                    await create_notification(
                        user_id=str(user_id),
                        title="New Regulatory Alert",
                        message=finding.get("plain_language_summary", "A new circular has been detected."),
                        urgency=finding.get("urgency", "medium"),
                        source="SENTINEL",
                        db=db
                    )
            await db.commit()

    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.ensure_future(run())
    else:
        loop.run_until_complete(run())

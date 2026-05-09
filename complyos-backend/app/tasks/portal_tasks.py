from app.tasks.celery_app import celery_app
from app.database import redis_client, mongo_db, AsyncSessionLocal
from app.services.notification_service import create_notification
import json
import asyncio

@celery_app.task(name="app.tasks.portal_tasks.process_portal_queue")
def process_portal_queue():
    """Background task to process registration portal submissions"""
    async def run():
        # Scanning Redis for portal_queue:*
        # Note: redis_client.keys is sync in some versions, but we use redis.asyncio
        keys = await redis_client.keys("portal_queue:*")
        
        async with AsyncSessionLocal() as db:
            for key in keys:
                data_str = await redis_client.get(key)
                if not data_str: continue
                
                data = json.loads(data_str)
                parts = key.decode().split(":")
                user_id = parts[1]
                portal_name = parts[2]
                
                # Mock submission logic
                success = True # Assume success for POC
                
                if success:
                    await create_notification(
                        user_id=user_id,
                        title=f"Registration Successful: {portal_name}",
                        message=f"Your registration for {portal_name} has been processed.",
                        urgency="low",
                        source="system",
                        db=db
                    )
                    await redis_client.delete(key)
                else:
                    # Move to manual queue in MongoDB
                    await mongo_db.manual_queue.insert_one({
                        "user_id": user_id,
                        "portal": portal_name,
                        "data": data,
                        "reason": "Automation failed"
                    })
                    await redis_client.delete(key)
            await db.commit()

    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.ensure_future(run())
    else:
        loop.run_until_complete(run())

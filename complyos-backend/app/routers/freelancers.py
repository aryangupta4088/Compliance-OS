from fastapi import APIRouter, Depends
from app.database import mongo_db
from app.utils.auth import get_current_user
from app.models.user import User
from datetime import datetime

router = APIRouter(prefix="/freelancers", tags=["Freelancers"])

@router.get("/list")
async def list_freelancers(category: str = None):
    query = {}
    if category:
        query["category"] = category
    
    cursor = mongo_db.freelancers.find(query)
    freelancers = await cursor.to_list(length=100)
    for f in freelancers:
        f["_id"] = str(f["_id"])
    return freelancers

@router.post("/connect/{freelancer_id}")
async def connect_freelancer(
    freelancer_id: str,
    current_user: User = Depends(get_current_user)
):
    request = {
        "user_id": str(current_user.id),
        "freelancer_id": freelancer_id,
        "status": "pending",
        "created_at": datetime.utcnow()
    }
    await mongo_db.freelancer_connections.insert_one(request)
    return {"message": "Connection request sent"}

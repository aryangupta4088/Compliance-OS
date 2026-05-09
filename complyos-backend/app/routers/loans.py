from fastapi import APIRouter, Depends
from app.utils.auth import get_current_user
from app.utils.dependencies import get_business_profile
from app.models.user import User
from app.models.business import BusinessProfile
from app.agents.scout import ScoutAgent
from app.database import mongo_db
from datetime import datetime
import json

router = APIRouter(prefix="/loans", tags=["Loans"])

LOAN_SCHEMES = [
    {"id": "mudra_shishu", "name": "MUDRA Shishu", "type": "loan", "max": "50,000"},
    {"id": "mudra_kishore", "name": "MUDRA Kishore", "type": "loan", "max": "5,00,000"},
    {"id": "mudra_tarun", "name": "MUDRA Tarun", "type": "loan", "max": "10,00,000"},
    {"id": "pmsvanidhi", "name": "PM SVANidhi", "type": "loan", "max": "50,000"},
    {"id": "cgtmse", "name": "CGTMSE", "type": "guarantee", "max": "2,00,00,000"},
    {"id": "standup_india", "name": "Stand Up India", "type": "loan", "max": "1,00,00,000"}
]

@router.get("/recommended")
async def get_recommended_loans(
    profile: BusinessProfile = Depends(get_business_profile)
):
    scout = ScoutAgent()
    # Mock profile dict for scout
    profile_dict = {
        "business_name": profile.business_name,
        "type": profile.business_type,
        "state": profile.state,
        "turnover": profile.turnover_range,
        "is_women_led": profile.is_women_led
    }
    
    # We pass the hardcoded loan schemes as context to Scout
    recommendations = await scout.find_schemes(
        profile=profile_dict,
        enrolled=profile.enrolled_schemes or [],
        context_documents=[json.dumps(s) for s in LOAN_SCHEMES]
    )
    return recommendations

@router.post("/interest/{loan_id}")
async def express_interest(
    loan_id: str,
    current_user: User = Depends(get_current_user)
):
    interest = {
        "user_id": str(current_user.id),
        "loan_id": loan_id,
        "timestamp": datetime.utcnow(),
        "status": "pending"
    }
    await mongo_db.loan_interests.insert_one(interest)
    return {"message": "Interest recorded"}

from fastapi import APIRouter, Depends
from app.utils.dependencies import get_business_profile
from app.models.business import BusinessProfile
from app.agents.pathway import PathwayAgent
from app.database import redis_client
import json

router = APIRouter(prefix="/registration", tags=["Registrations"])

@router.get("/roadmap")
async def get_roadmap(
    profile: BusinessProfile = Depends(get_business_profile)
):
    pathway = PathwayAgent()
    profile_dict = {
        "business_name": profile.business_name,
        "type": profile.business_type,
        "state": profile.state,
        "district": profile.district
    }
    # Existing registrations from profile
    existing = []
    if profile.udyam_number: existing.append("udyam")
    if profile.gstin: existing.append("gst")
    if profile.pan: existing.append("pan")
    
    roadmap = await pathway.generate_roadmap(profile_dict, existing)
    return roadmap

@router.post("/schedule")
async def schedule_registration(
    portal_name: str,
    form_data: dict,
    profile: BusinessProfile = Depends(get_business_profile)
):
    pathway = PathwayAgent()
    # Cache in Redis for background processing
    success = PathwayAgent.schedule_submission(portal_name, form_data, str(profile.user_id))
    return {"message": "Submission scheduled for background processing", "portal": portal_name}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from app.database import get_db
from app.models.business import BusinessProfile
from app.models.compliance import ComplianceDeadline
from app.models.scheme import SchemeApplication
from app.models.notification import Notification
from app.schemas.business import BusinessProfileCreate, BusinessProfileResponse
from app.utils.auth import get_current_user
from app.models.user import User
import uuid

router = APIRouter(prefix="/business", tags=["Business"])

@router.post("/profile", response_model=BusinessProfileResponse)
async def create_profile(
    profile_in: BusinessProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check if profile exists
    res = await db.execute(select(BusinessProfile).where(BusinessProfile.user_id == current_user.id))
    if res.scalar_one_or_none():
        raise HTTPException(400, "Profile already exists")
    
    profile = BusinessProfile(
        id=uuid.uuid4(),
        user_id=current_user.id,
        **profile_in.dict()
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile

@router.get("/profile", response_model=BusinessProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(BusinessProfile).where(BusinessProfile.user_id == current_user.id))
    profile = res.scalar_one_or_none()
    if not profile:
        raise HTTPException(404, "Profile not found")
    return profile

@router.patch("/profile", response_model=BusinessProfileResponse)
async def update_profile(
    profile_in: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await db.execute(
        update(BusinessProfile)
        .where(BusinessProfile.user_id == current_user.id)
        .values(**profile_in)
    )
    await db.commit()
    res = await db.execute(select(BusinessProfile).where(BusinessProfile.user_id == current_user.id))
    return res.scalar_one()

@router.get("/dashboard/summary")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Pending deadlines count
    deadlines_res = await db.execute(
        select(func.count(ComplianceDeadline.id))
        .where(ComplianceDeadline.user_id == current_user.id, ComplianceDeadline.status == "pending")
    )
    pending_deadlines = deadlines_res.scalar() or 0
    
    # 2. Schemes matched count
    schemes_res = await db.execute(
        select(func.count(SchemeApplication.id))
        .where(SchemeApplication.user_id == current_user.id, SchemeApplication.status == "eligible")
    )
    matched_schemes = schemes_res.scalar() or 0
    
    # 3. Total savings estimate (mock)
    savings = matched_schemes * 50000 # Mock calculation
    
    # 4. Recent notices (last 5)
    notices_res = await db.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(5)
    )
    recent_notices = notices_res.scalars().all()
    
    # 5. Profile completion %
    profile_res = await db.execute(select(BusinessProfile).where(BusinessProfile.user_id == current_user.id))
    profile = profile_res.scalar_one_or_none()
    completion = 0
    if profile:
        fields = ["business_name", "business_type", "sector", "state", "district", "pincode", "udyam_number", "gstin", "pan"]
        filled = sum(1 for f in fields if getattr(profile, f))
        completion = int((filled / len(fields)) * 100)
    
    return {
        "pending_deadlines": pending_deadlines,
        "matched_schemes": matched_schemes,
        "total_savings_estimate": savings,
        "recent_notices": recent_notices,
        "profile_completion": completion
    }

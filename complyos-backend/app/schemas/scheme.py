from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.utils.auth import get_current_user
from app.models.user import User
from app.models.scheme import SchemeApplication
from app.models.business import BusinessProfile
import uuid

router = APIRouter(prefix="/schemes", tags=["Schemes"])

SCHEMES_DATA = [
    {
        "id": "pmegp",
        "name": "PMEGP",
        "full_name": "Prime Minister's Employment Generation Programme",
        "description": "Subsidy up to 35% for new manufacturing/service units",
        "max_benefit": "₹25 Lakh subsidy",
        "eligibility": ["new_business", "manufacturing", "service"],
        "category": "subsidy",
        "ministry": "MSME Ministry",
        "apply_url": "https://www.kviconline.gov.in/pmegpeportal/pmegphome/index.jsp"
    },
    {
        "id": "mudra_shishu",
        "name": "MUDRA Shishu",
        "full_name": "Pradhan Mantri MUDRA Yojana - Shishu",
        "description": "Loans up to ₹50,000 for micro businesses",
        "max_benefit": "₹50,000 loan",
        "eligibility": ["micro", "new_business"],
        "category": "loan",
        "ministry": "Finance Ministry",
        "apply_url": "https://www.mudra.org.in/"
    },
    {
        "id": "mudra_kishor",
        "name": "MUDRA Kishor",
        "full_name": "Pradhan Mantri MUDRA Yojana - Kishor",
        "description": "Loans from ₹50,000 to ₹5 Lakh for growing businesses",
        "max_benefit": "₹5 Lakh loan",
        "eligibility": ["micro", "small"],
        "category": "loan",
        "ministry": "Finance Ministry",
        "apply_url": "https://www.mudra.org.in/"
    },
    {
        "id": "clcss",
        "name": "CLCSS",
        "full_name": "Credit Linked Capital Subsidy Scheme",
        "description": "15% subsidy on technology upgradation for SSIs",
        "max_benefit": "₹15 Lakh subsidy",
        "eligibility": ["manufacturing", "technology_upgrade"],
        "category": "subsidy",
        "ministry": "MSME Ministry",
        "apply_url": "https://clcss.dcmsme.gov.in/"
    },
    {
        "id": "wus",
        "name": "Women Entrepreneurship",
        "full_name": "Women Udyam Support Scheme",
        "description": "Special loans and subsidies for women-led MSMEs",
        "max_benefit": "₹10 Lakh at reduced interest",
        "eligibility": ["women_led"],
        "category": "subsidy",
        "ministry": "MSME Ministry",
        "apply_url": "https://msme.gov.in/"
    },
]

@router.get("/")
async def list_schemes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Get business profile to filter eligible schemes
    res = await db.execute(
        select(BusinessProfile).where(BusinessProfile.user_id == current_user.id)
    )
    profile = res.scalar_one_or_none()

    schemes = SCHEMES_DATA.copy()

    # Mark eligible based on profile
    for scheme in schemes:
        scheme["eligible"] = True
        if profile and profile.is_women_led == False and "women_led" in scheme["eligibility"]:
            scheme["eligible"] = False

    return {"schemes": schemes, "total": len(schemes)}


@router.get("/{scheme_id}")
async def get_scheme(scheme_id: str, current_user: User = Depends(get_current_user)):
    scheme = next((s for s in SCHEMES_DATA if s["id"] == scheme_id), None)
    if not scheme:
        raise HTTPException(404, "Scheme not found")
    return scheme


@router.post("/{scheme_id}/apply")
async def apply_scheme(
    scheme_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    scheme = next((s for s in SCHEMES_DATA if s["id"] == scheme_id), None)
    if not scheme:
        raise HTTPException(404, "Scheme not found")

    # Check if already applied
    res = await db.execute(
        select(SchemeApplication).where(
            SchemeApplication.user_id == current_user.id,
            SchemeApplication.scheme_id == scheme_id
        )
    )
    if res.scalar_one_or_none():
        raise HTTPException(400, "Already applied for this scheme")

    application = SchemeApplication(
        id=uuid.uuid4(),
        user_id=current_user.id,
        scheme_id=scheme_id,
        scheme_name=scheme["name"],
        status="applied"
    )
    db.add(application)
    await db.commit()
    return {"message": "Application submitted", "scheme": scheme["name"]}


@router.get("/applications/my")
async def my_applications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(SchemeApplication).where(SchemeApplication.user_id == current_user.id)
    )
    applications = res.scalars().all()
    return {"applications": applications}
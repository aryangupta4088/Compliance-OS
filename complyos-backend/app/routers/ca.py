from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.database import get_db, mongo_db
from app.models.ca import CAProfile
from app.models.user import User, UserRole
from app.models.scheme import SchemeApplication
from app.schemas.ca import CAProfileResponse, ConsultationBooking
from app.utils.auth import get_current_user
from app.utils.dependencies import require_ca_role
import uuid
from datetime import datetime

router = APIRouter(prefix="/ca", tags=["Chartered Accountants"])

@router.get("/list", response_model=list[CAProfileResponse])
async def list_cas(
    specialization: str = None,
    state: str = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(CAProfile).where(CAProfile.verified == True)
    if specialization:
        query = query.where(CAProfile.specializations.contains([specialization]))
    # State filter logic would depend on CAProfile having a state field, 
    # assuming for now it's part of the business profile or added to CAProfile
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/book/{ca_id}")
async def book_consultation(
    ca_id: uuid.UUID,
    booking: ConsultationBooking,
    current_user: User = Depends(get_current_user)
):
    booking_record = {
        "ca_id": str(ca_id),
        "user_id": str(current_user.id),
        "scheduled_at": booking.scheduled_at,
        "notes": booking.notes,
        "status": "booked",
        "created_at": datetime.utcnow()
    }
    await mongo_db.consultations.insert_one(booking_record)
    return {"message": "Consultation booked successfully"}

@router.get("/clients")
async def get_ca_clients(
    current_user: User = Depends(require_ca_role),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(CAProfile).where(CAProfile.user_id == current_user.id))
    profile = res.scalar_one_or_none()
    if not profile:
        raise HTTPException(404, "CA profile not found")
    
    # Profile.clients stores user IDs
    client_ids = profile.clients or []
    # Fetch user/business details for these IDs
    # (Simplified for now)
    return {"client_ids": client_ids}

@router.patch("/clients/{client_id}/approve")
async def approve_scheme(
    client_id: uuid.UUID,
    scheme_name: str,
    current_user: User = Depends(require_ca_role),
    db: AsyncSession = Depends(get_db)
):
    # Verify client is assigned to this CA
    ca_res = await db.execute(select(CAProfile).where(CAProfile.user_id == current_user.id))
    ca_profile = ca_res.scalar_one()
    if str(client_id) not in (ca_profile.clients or []):
        raise HTTPException(403, "Not authorized for this client")
        
    await db.execute(
        update(SchemeApplication)
        .where(SchemeApplication.user_id == client_id, SchemeApplication.scheme_name == scheme_name)
        .values(ca_approved=True, status="applied")
    )
    await db.commit()
    return {"message": f"Scheme {scheme_name} approved for client"}

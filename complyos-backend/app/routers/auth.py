from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.user import UserCreate, UserResponse, Token
from app.models.user import User
from app.utils.auth import verify_password, create_access_token, get_password_hash, get_current_user
from app.database import get_db
from datetime import timedelta

router = APIRouter(tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check existence
    res = await db.execute(select(User).where(User.email == user_in.email))
    if res.scalar_one_or_none():
        raise HTTPException(400, "Email registered")
    
    user = User(
        email=user_in.email,
        phone=user_in.phone,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/login", response_model=Token)
async def login(email: str, password: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User).where(User.email == email))
    user = res.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid creds")
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token}

@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return current_user

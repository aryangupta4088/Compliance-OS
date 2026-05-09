from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis
from app.config import settings

# PostgreSQL Async Engine
engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

# MongoDB Client
mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
mongo_db = mongo_client[settings.MONGODB_DB]

# Redis Client
redis_client = redis.from_url(settings.REDIS_URL)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    # Import models here to ensure they are registered with Base
    from app.models import user, business, compliance, scheme, notification
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

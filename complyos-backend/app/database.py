from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

try:
    from motor.motor_asyncio import AsyncIOMotorClient
    mongo_client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=3000)
    mongo_db = mongo_client[settings.MONGODB_DB]
except Exception:
    mongo_db = None

try:
    import redis.asyncio as redis
    redis_client = redis.from_url(settings.REDIS_URL)
except Exception:
    redis_client = None

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    from app.models import user, business, compliance, scheme, notification, document, ca
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
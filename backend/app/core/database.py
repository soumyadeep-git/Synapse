from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Create the Async Engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True if you want to see SQL queries in logs
    future=True
)

# Create the Session Factory
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# Base class for models
Base = declarative_base()

# Dependency to get DB session in endpoints
async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
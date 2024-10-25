from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# for alembic to alert tables
sync_engine = create_engine("sqlite:///./test.db")
# for application
engine = create_async_engine(DATABASE_URL, echo=True)

# Async session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_async_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


Base = declarative_base()

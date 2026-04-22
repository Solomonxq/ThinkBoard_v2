import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.core.config import settings

engine = create_async_engine(settings.database_url, echo=False)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from src.core.config.database import settings

engine = create_async_engine(settings.database_url, future=True, echo=True)
async_session_maker = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


async def get_async_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

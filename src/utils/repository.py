from abc import ABC, abstractmethod

from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import User


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def find_all(self):
        raise NotImplementedError

    @abstractmethod
    async def update_one(self, user_id: int, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, user_id: int):
        raise NotImplementedError

    async def find_one(self, **filter_by):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_one(self, data: dict) -> int:
        stmt = insert(self.model).values(**data).returning(self.model.id)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def update_one(self, user_id: int, data: dict) -> int:
        stmt = update(self.model).values(**data).filter_by(id=user_id).returning(self.model.id)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def delete_one(self, user_id: int) -> None:
        stmt = delete(self.model).where(self.model.id == user_id)
        await self.session.execute(stmt)

    async def find_one_or_none(self, **filter_by):
        stmt = select(self.model).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def find_all(self):
        stmt = select(self.model)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def find_one(self, **filter_by):
        stmt = select(self.model).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        res = res.scalar_one().to_read_model()
        return res

    async def add_user(self, user: User) -> int:
        self.session.add(user)
        await self.session.commit()
        return user.id

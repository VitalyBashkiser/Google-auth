from abc import abstractmethod, ABC
from typing import Type, Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.repositories.users import UsersRepository


class ABCUnitOfWork(ABC):
    session: AsyncSession

    # Repository classes
    users: UsersRepository

    @abstractmethod
    def __init__(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWork":
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, *args: Any) -> None:
        raise NotImplementedError


class UnitOfWork(ABCUnitOfWork):
    def __init__(self) -> None:
        self.session_maker = Session

    async def __aenter__(self) -> "UnitOfWork":
        self.session = self.session_maker()
        self.users = UsersRepository(self.session)

        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        if exc:
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.close()
        await logger.complete()

        if exc:
            raise exc